/*
 * Copyright 2021 Swiss Data Science Center (SDSC)
 * A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
 * Eidgenössische Technische Hochschule Zürich (ETHZ).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ch.renku.acceptancetests.tooling

import cats.effect.IO._
import cats.effect.{ContextShift, IO}
import ch.renku.acceptancetests.model.{AuthorizationToken, BaseUrl}
import io.circe.Json
import io.circe.optics.JsonPath
import io.circe.optics.JsonPath.root
import org.http4s._
import org.http4s.circe._
import org.http4s.client.blaze.BlazeClientBuilder
import org.http4s.client.dsl.Http4sClientDsl
import org.scalatest.Assertions.fail

import scala.concurrent.ExecutionContext

trait RestClient extends Http4sClientDsl[IO] {

  val jsonRoot: JsonPath = root

  private implicit lazy val contextShift: ContextShift[IO] = IO.contextShift(ExecutionContext.global)

  private lazy val clientBuilder = BlazeClientBuilder[IO](ExecutionContext.global)

  def GET(baseUrl: BaseUrl): Request[IO] = Request[IO](
    Method.GET,
    uri = Uri.fromString(baseUrl.toString).fold(error => fail(error.getMessage()), identity)
  )

  def POST(baseUrl: BaseUrl): Request[IO] = Request[IO](
    Method.POST,
    Uri.fromString(baseUrl.toString).fold(error => fail(error.getMessage()), identity)
  )

  def DELETE(baseUrl: BaseUrl): Request[IO] = Request[IO](
    Method.DELETE,
    uri = Uri.fromString(baseUrl.toString).fold(error => fail(error.getMessage()), identity)
  )

  implicit class RequestOps(request: Request[IO]) {

    def withAuthorizationToken(authorizationToken: AuthorizationToken): Request[IO] =
      request.withHeaders(Headers of authorizationToken.asHeader)

    def send: (Request[IO], Response[IO]) =
      request -> clientBuilder.resource.use(client => client.run(request).use(IO.pure)).unsafeRunSync()
  }

  implicit class ResponseOps(reqAndResp: (Request[IO], Response[IO])) {
    private lazy val (request, response) = reqAndResp

    def whenReceived(status: Status): (Request[IO], Response[IO]) =
      if (response.status == status) reqAndResp
      else
        fail(
          s"${request.method} ${request.uri} returned ${response.status} which is not expected $status"
        )

    lazy val responseStatus: Status = response.status

    def expect(status: Status, otherwiseLog: String): Unit =
      if (response.status != status)
        fail(
          s"$otherwiseLog -> ${request.method} ${request.uri} returned ${response.status} which is not expected $status"
        )

    def bodyAsJson: Json = response.as[Json].unsafeRunSync()
  }

  implicit class JsonOps(json: Json) {

    def extract[V](extractor: Json => V): V = extractor(json)

  }
}
