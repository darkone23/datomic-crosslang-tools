package example

class HelloSpec extends munit.FunSuite {
  test("say hello to jimi") {
    assertEquals(Hello.QUERY_INPUT, "Jimi Hendrix")
  }
}
