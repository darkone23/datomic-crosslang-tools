package example

import scala.annotation.nowarn

import example.DatomicFns

@nowarn("msg=non-variable type argument")
object Hello extends Greeting with App {

  val conn = DatomicFns.connect(
    s"datomic:sql://${DATOMIC_DB_NAME}?jdbc:postgresql://${PG_ADDRESS}/${PG_DATABASE}?user=${PG_USER}&password=${PG_PASS}"
  )

  val db = DatomicFns.db(conn)

  val result = DatomicFns.q(QUERY, db, QUERY_INPUT)

  result.items()

  System.exit(0)

}

trait Greeting {

val QUERY = """
  [:find ?id ?type ?gender
   :in $ ?name
   :where
  		[?e :artist/name ?name]
			[?e :artist/gid ?id]
			[?e :artist/type ?teid]
			[?teid :db/ident ?type]
      [?e :artist/gender ?geid]
      [?geid :db/ident ?gender]]
					"""

  val QUERY_INPUT = "Jimi Hendrix"

  val DATOMIC_DB_NAME = "my-datomic-database"

  val PG_ADDRESS = "localhost:5432"
  val PG_DATABASE = "my-datomic-storage"

  val PG_USER = "datomic-user"
  val PG_PASS = "unsafe"

}
