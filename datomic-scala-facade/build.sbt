import Dependencies._

import sbt.Keys.{version, _}
import sbt.librarymanagement.Resolver.mavenLocal

ThisBuild / scalaVersion     := "2.13.12"
ThisBuild / version          := "0.1.0-SNAPSHOT"
ThisBuild / organization     := "dev.langnet"
ThisBuild / organizationName := "langnet"
ThisBuild / assemblyShadeRules := Seq(
  ShadeRule.rename("org.apache.commons.io.**" -> "shadeio.@1").inAll
)
ThisBuild / assemblyMergeStrategy := {
    case "COPYRIGHT" => MergeStrategy.discard
    case "module-info.class" => MergeStrategy.discard
    case x if Assembly.isConfigFile(x) =>
      MergeStrategy.concat
    case PathList(ps @ _*) if Assembly.isReadme(ps.last) || Assembly.isLicenseFile(ps.last) =>
      MergeStrategy.rename
    case PathList("org", "apache", "commons", "logging", xs @ _*) =>
      (xs map {_.toLowerCase}) match {
  			case _ => MergeStrategy.first
      }
  	case PathList("META-INF", xs @ _*) =>
      (xs map {_.toLowerCase}) match {
        case ("manifest.mf" :: Nil) | ("index.list" :: Nil) | ("dependencies" :: Nil) =>
          MergeStrategy.discard
        case ps @ (x :: xs) if ps.last.endsWith(".sf") || ps.last.endsWith(".dsa") =>
          MergeStrategy.discard
        case "plexus" :: xs =>
          MergeStrategy.discard
        case ("io.netty.versions.properties" :: Nil) =>
          MergeStrategy.concat
        case "services" :: xs =>
          MergeStrategy.filterDistinctLines
        case ps @ (x :: xs) if ps.last.equals("module-info.class") =>
          MergeStrategy.discard
        case ("spring.schemas" :: Nil) | ("spring.handlers" :: Nil) =>
          MergeStrategy.filterDistinctLines
        case _ => MergeStrategy.deduplicate
      }
    case _ => MergeStrategy.deduplicate
  }

Compile / PB.targets := Seq(
  scalapb.gen() -> (Compile / sourceManaged).value / "scalapb"
)

// (optional) If you need scalapb/scalapb.proto or anything from
// google/protobuf/*.proto

lazy val root = (project in file("."))
  .settings(
    assembly / mainClass := Some("example.Hello"),
    name := "datomic-scala-facade",
    resolvers ++= Seq(
      mavenLocal,
      ("datomic" at "http://files.datomic.com/maven").withAllowInsecureProtocol(true),
      ("clojars" at "http://clojars.org/repo").withAllowInsecureProtocol(true),
      // ("ICM repository" at "http://maven.icm.edu.pl/artifactory/repo/").withAllowInsecureProtocol(true)
    ),
    libraryDependencies ++= Seq(
      munit % Test,
      "com.thesamet.scalapb" %% "scalapb-runtime" % scalapb.compiler.Version.scalapbVersion % "protobuf",
      "org.clojure" % "clojure" % "1.12.0",
      "com.datomic" % "peer" % "1.0.7187",
      "com.datomic" % "client-pro" % "1.0.81",
      "com.cognitect" % "transit-clj" % "1.0.333",
      "org.postgresql" % "postgresql" % "42.7.4"
		)
	// ).settings(
	//   artifact in (Compile, assembly) ~= { art =>
 //      art.copy(`classifier` = Some("assembly"))
 //    }
 
  // ).settings(
  )


// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for instructions on how to publish to Sonatype.
publishTo := {
  val nexus = "https://my.nexusurl.here/"
  if (isSnapshot.value)
    Some("snapshots" at nexus + "repository/maven-snapshots")
  else
    Some("releases"  at nexus + "repository/maven-releases")
}

ThisBuild / publishMavenStyle := true

assembly / artifact := {
  val art = (assembly / artifact).value
  art.withClassifier(Some("assembly"))
}

assembly / assemblyJarName := s"${name.value}-${version.value}.jar"

addArtifact(assembly / artifact, assembly)

Compile / packageBin / publishArtifact := false
Compile / packageDoc / publishArtifact := false
Compile / packageSrc / publishArtifact := false

credentials += Credentials(
  "Sonatype Nexus Repository Manager",
  "my.nexusurl.here",
  "my-nexususer-here",
  "my-nexuspass-here"
)
