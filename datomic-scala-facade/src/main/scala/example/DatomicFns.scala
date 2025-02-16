
package example

import scala.jdk.CollectionConverters._

import clojure.java.api.Clojure

case class DatomicConnection(connect: String, _clj: java.lang.Object)
case class DatomicDatabase(conn: DatomicConnection, _clj: java.lang.Object)
case class DatomicQResult(query:String, db: DatomicDatabase, input: String, _clj: java.lang.Object) {
  def items(): Int = {
    var num = 0
    _clj match {
      case hash: java.util.HashSet[clojure.lang.PersistentVector] => {
        println("looking at results...")
        for (item <- hash.iterator().asScala) {
          num += 1
          println(item)
        }
      }
      case s: java.lang.String => {
        println("looking at encoded results...")
        println(s)
      }
      case _ => {
        println("Unexpected result!")
        println(_clj)
        println(_clj.getClass())
      }
    }
    return num
  }
}

object DatomicFns {

  private def __init_clj(): (String, String) => clojure.lang.IFn = {
    val require = Clojure.`var`("clojure.core", "require");
    require.invoke(Clojure.read("datomic.api"));
    require.invoke(Clojure.read("cognitect.transit"));
    def fn(a: String, b: String): clojure.lang.IFn = {
      return Clojure.`var`(a, b)
    }
    return fn
  }

  lazy private val clj_var = __init_clj()

  lazy private val conn_fn = clj_var("datomic.api", "connect")
  lazy private val db_fn = clj_var("datomic.api", "db")
  lazy private val q_fn = clj_var("datomic.api", "q")

  private object TransitFns {
    lazy val writer_fn = clj_var("cognitect.transit", "writer")
    lazy val write_fn = clj_var("cognitect.transit", "write")
    lazy val json_mode = Clojure.read(":json")

    def write(obj: java.lang.Object): String = {
      // return 
      val baos = new java.io.ByteArrayOutputStream(4096)
    	val writer = DatomicFns.TransitFns.writer_fn.invoke(baos, DatomicFns.TransitFns.json_mode);
    	DatomicFns.TransitFns.write_fn.invoke(writer, obj)
    	return baos.toString()
    }
  }

  def connect(connect_str: String): DatomicConnection = {
    println("making conn", connect_str)
    val conn = DatomicFns.conn_fn.invoke(connect_str)
    return DatomicConnection(connect_str, conn)
  }

  def db(conn: DatomicConnection): DatomicDatabase = {
    println("making db")
    val db = DatomicFns.db_fn.invoke(conn._clj)
    return DatomicDatabase(conn, db)
  }

  def q(query:String, db: DatomicDatabase, input: String): DatomicQResult = {
    println("running query")
    println(query)
    println(s"Where name = '${input}'")
    val result = DatomicFns.q_fn.invoke(query, db._clj, input)
    val result_json = DatomicFns.TransitFns.write(result)
    return DatomicQResult(query, db, input, result_json)
  }

}
