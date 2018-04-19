# -*- coding: utf-8 -*-
#
# Copyright 2018 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Implement integration for using GitLab repositories."""

import os
from urllib.parse import urlsplit, urlunsplit

import docker
from tornado import gen, web


class SpawnerMixin():
    """Extend spawner methods."""

    @gen.coroutine
    def git_repository(self):
        """Return the URL of current repository."""
        auth_state = yield self.user.get_auth_state()

        options = self.user_options
        namespace = options.get('namespace')
        project = options.get('project')

        url = os.environ.get('GITLAB_HOST', 'http://gitlab.renga.local')

        scheme, netloc, path, query, fragment = urlsplit(url)

        repository = urlunsplit((
            scheme, 'oauth2:' + auth_state['access_token'] + '@' + netloc,
            path + '/' + namespace + '/' + project + '.git', query, fragment
        ))

        return repository

    def get_env(self):
        """Extend environment variables passed to the notebook server."""
        # TODO how to get the async result here?
        #      repository = yield from self.git_repository()

        environment = super().get_env()
        environment.update({
            # 'CI_REPOSITORY_URL': repository,
            'CI_NAMESPACE':
                self.user_options.get('namespace', ''),
            'CI_PROJECT':
                self.user_options.get('project', ''),
            'CI_ENVIRONMENT_SLUG':
                self.user_options.get('environment_slug', ''),
            'CI_COMMIT_SHA':
                self.user_options.get('commit_sha', ''),
            'GITLAB_HOST':
                os.environ.get('GITLAB_HOST', 'http://gitlab.renga.build'),
        })
        return environment

    @gen.coroutine
    def start(self, *args, **kwargs):
        """Start the notebook server."""
        self.log.info(
            "starting with args: {}".format(' '.join(self.get_args()))
        )
        self.log.info("user options: {}".format(self.user_options))

        auth_state = yield self.user.get_auth_state()
        assert 'access_token' in auth_state
        self.log.info(auth_state)

        # 1. check authorization against GitLab
        options = self.user_options
        namespace = options.get('namespace')
        project = options.get('project')
        env_slug = options.get('environment_slug')

        url = os.getenv('GITLAB_HOST', 'http://gitlab.renga.build')

        import gitlab
        gl = gitlab.Gitlab(
            url, api_version=4, oauth_token=auth_state['access_token']
        )

        try:
            gl_project = gl.projects.get('{0}/{1}'.format(namespace, project))
            gl_user = gl.users.list(username=self.user.name)[0]
            access_level = gl_project.members.get(gl_user.id).access_level
        except Exception as e:
            self.log.error(e)
            raise web.HTTPError(401, 'Not authorized to view project.')
            return

        if access_level < gitlab.DEVELOPER_ACCESS:
            raise web.HTTPError(401, 'Not authorized to view project.')
            return

        if not any(
            gl_env.slug for gl_env in gl_project.environments.list()
            if gl_env.slug == env_slug
        ):
            raise web.HTTPError(404, 'Environment does not exist.')
            return

        self.image = '{image_registry}'\
                     '/{namespace}'\
                     '/{project}'\
                     '/{environment_slug}'\
                     ':{commit_sha}'.format(image_registry=os.getenv('IMAGE_REGISTRY'), **options)
        self.log.info(self.image)

        try:
            result = yield super().start(*args, **kwargs)
        except docker.errors.ImageNotFound:
            self.log.info(
                'Image {0} not found - using default image.'.
                format(self.image)
            )
            self.image = os.getenv(
                'JUPYTERHUB_NOTEBOOK_IMAGE', 'jupyter/minimal-notebook'
            )
            result = yield super().start(*args, **kwargs)

        return result


try:
    from dockerspawner import DockerSpawner

    class RepoVolume(DockerSpawner):
        """Create and configure repo volume."""

        @gen.coroutine
        def start(self):
            """Create init container."""
            options = self.user_options
            container_name = 'init-' + self.name  # TODO user namespace?
            name = self.name + '-git-repo'
            volume_name = 'repo-' + container_name
            volume_path = '/repo'

            try:
                yield self.docker(
                    'remove_container', container_name, force=True
                )
            except Exception as e:
                self.log.error(e)

            try:
                yield self.docker('remove_volume', volume_name, force=True)
            except Exception as e:
                self.log.error(e)

            host_config = yield self.docker(
                'create_host_config',
                network_mode=self.network_name,
                binds={
                    volume_name: {
                        'bind': volume_path,
                        'mode': 'rw',
                    },
                },
            )

            volume = yield self.docker('create_volume', name=volume_name)
            self.log.info(volume)

            # 1. clone the repo
            # 2. checkout the environment branch and commit sha
            # 3. set jovyan as owner
            repository = yield self.git_repository()
            container = yield self.docker(
                'create_container',
                'alpine/git',
                name=container_name,
                entrypoint='sh -c',
                command=[
                    'git clone {repository} {volume_path} && '
                    'git checkout -b {environment_slug} {commit_sha} && '
                    'chown 1000:100 -Rc {volume_path}'.format(
                        commit_sha=options.get('commit_sha'),
                        environment_slug=options.get('environment_slug'),
                        repository=repository,
                        volume_path=volume_path,
                    ),
                    volume_path,
                ],
                volumes=[volume_path],
                working_dir=volume_path,
                host_config=host_config,
            )
            started = yield self.docker('start', container=container.get('Id'))
            wait = yield self.docker('wait', container=container)
            self.log.info(wait)

            # TODO remove the container?
            # yield self.docker(
            #     'remove_container', container.get('Id'), force=True)

            self.log.info(container)

            environment = self.get_env()
            environment['CI_REPOSITORY_URL'] = repository

            extra_create_kwargs = {
                'working_dir': volume_path,
                'environment': environment,
                'volumes': [volume_path],
            }
            extra_host_config = {
                'binds': {
                    volume_name: {
                        'bind': volume_path,
                        'mode': 'rw',
                    },
                },
            }

            result = yield super().start(
                extra_create_kwargs=extra_create_kwargs,
                extra_host_config=extra_host_config,
            )
            return result

    class RengaDockerSpawner(SpawnerMixin, RepoVolume, DockerSpawner):
        """A class for spawning notebooks on Renga-JupyterHub using Docker."""

except ImportError:
    pass

try:
    from kubespawner import KubeSpawner

    class RengaKubeSpawner(SpawnerMixin, KubeSpawner):
        """A class for spawning notebooks on Renga-JupyterHub using K8S."""

        @gen.coroutine
        def get_pod_manifest(self):
            """Include volume with the git repository."""
            auth_state = yield self.user.get_auth_state()
            repository = yield self.git_repository()
            options = self.user_options

            # https://gist.github.com/tallclair/849601a16cebeee581ef2be50c351841
            container_name = 'init-' + self.pod_name
            name = self.pod_name + '-git-repo'

            #: Define new empty volume.
            volume = {
                'name': name,
                'emptyDir': {},
            }
            self.volumes.append(volume)

            #: Define volume mount for both init and notebook container.
            volume_mount = {
                'mountPath': self.notebook_dir,
                'name': name,
            }

            #: Define an init container.
            self.singleuser_init_containers = self.singleuser_init_containers or []
            self.singleuser_init_containers.append({
                'name':
                    container_name,
                'image':
                    'alpine/git',
                'args': [
                    'clone',
                    '--single-branch',
                    '-b',
                    self.git_revision,
                    '--',
                    repository,
                    '/repo',
                ],
                'volumeMounts': [volume_mount],
            })

            #: Share volume mount with notebook.
            self.volume_mounts.append(volume_mount)

            pod = yield super().get_pod_manifest()
            return pod

except ImportError:
    pass
