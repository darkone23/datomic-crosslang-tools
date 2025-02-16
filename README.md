tools used:

- [clojure](https://clojure.org/index)
- [datomic](https://docs.datomic.com/datomic-overview.html)
- [transit](https://cognitect.com/blog/2014/7/22/transit)
- [scala](https://docs.scala-lang.org/tour/tour-of-scala.html)
- [sbt-assembly](https://index.scala-lang.org/sbt/sbt-assembly)
- [rust](https://doc.rust-lang.org/stable/book/ch00-00-introduction.html)
- [j4rs](https://github.com/astonbitecode/j4rs)
- [maturin](https://www.maturin.rs/)
- [python](https://www.python.org/doc/)

what is happening?

according to [the docs](https://docs.datomic.com/reference/rest.html) datomic wants an embedded client
this uses rust (via maturin & j4rs) to embed a datomic jvm in a python applications

it uses transit to handle data serialization between datomic and python

very much a work in progress
