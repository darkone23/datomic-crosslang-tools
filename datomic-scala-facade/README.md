using scala assembly tools to ship onejar

datomic provides a clojure native api

use scala to define java interface

```sh
# assuming you have the musicbrainz db from the docker datomic demo
devenv shell
sbt run

sbt assembly
java -cp ./target/scala-2.13/datomic-scala-facade-0.1.0-SNAPSHOT.jar example.Hello

# and if you are wanting to copy manually for maturin testing
mkdir -p /tmp/datomic-crosslang-tools/jassets
cp ./target/scala-2.13/datomic-scala-facade-0.1.0-SNAPSHOT.jar /tmp/datomic-crosslang-tools/jassets 
```
