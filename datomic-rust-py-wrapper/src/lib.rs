use pyo3::prelude::*;
use rand::Rng;
use std::cmp::Ordering;
use std::io;

use j4rs::{ClasspathEntry, Instance, InvocationArg, Jvm, JvmBuilder};

#[pyfunction]
pub fn hello() {
    // this needs to be run NOT inside pyo3...
    //   installer prep work
    // Jvm::copy_j4rs_libs_under("/tmp/myapp").expect("copied the deps");

    // wget https://thoth.langnet.dev/repository/maven-snapshots/dev/langnet/datomic-grpc_2.13/0.1.0-SNAPSHOT/datomic-grpc_2.13-0.1.0-SNAPSHOT-assembly.jar

    let entry = ClasspathEntry::new(
        "/tmp/datomic-crosslang-tools/jassets/datomic-scala-facade-0.1.0-SNAPSHOT.jar",
    );

    let jvm = JvmBuilder::new()
        .with_base_path("/tmp/datomic-crosslang-tools")
        .classpath_entry(entry)
        .build()
        .expect("got the jvm");

    // let i1 = InvocationArg::try_from("a str").expect("got the java arg");
    let conn_str_arg = InvocationArg::try_from("datomic:sql://my-datomic-database?jdbc:postgresql://localhost:5432/my-datomic-storage?user=datomic-user&password=unsafe").expect("got conn arg");

    let conn_instance = jvm
        .invoke_static("example.DatomicFns", "connect", &[conn_str_arg])
        .expect("ran my conn method");

    let conn_arg = InvocationArg::try_from(conn_instance).expect("got conn arg");

    let db_instance = jvm
        .invoke_static("example.DatomicFns", "db", &[conn_arg])
        .expect("ran my db method");

    let db_arg = InvocationArg::try_from(db_instance).expect("got db arg");
    let query_arg = InvocationArg::try_from(
        "[:find ?id ?type ?gender \
          :in $ ?name \
          :where \
  		    [?e :artist/name ?name] \
			[?e :artist/gid ?id] \
			[?e :artist/type ?teid] \
			[?teid :db/ident ?type] \
            [?e :artist/gender ?geid] \
            [?geid :db/ident ?gender]]",
    )
    .expect("got query arg");
    let input_arg = InvocationArg::try_from("Jimi Hendrix").expect("got input arg");

    let q_instance = jvm
        .invoke_static("example.DatomicFns", "q", &[query_arg, db_arg, input_arg])
        .expect("ran my q method");

    let string_size: isize = jvm
        .chain(&q_instance)
        .expect("made a chain")
        .invoke("items", InvocationArg::empty())
        .expect("made a chain")
        .to_rust()
        .expect("invoke was cool");

    println!(
        "The JVM said the string size of: 'a str' was {}",
        string_size
    );

    // println!("Guess the number!");

    // let secret_number = rand::rng().random_range(1..101);

    // loop {
    //     println!("Please input your guess.");

    //     let mut guess = String::new();

    //     io::stdin()
    //         .read_line(&mut guess)
    //         .expect("Failed to read line");

    //     let guess: u32 = match guess.trim().parse() {
    //         Ok(num) => num,
    //         Err(_) => continue,
    //     };

    //     println!("You guessed: {}", guess);

    //     match guess.cmp(&secret_number) {
    //         Ordering::Less => println!("Too small!"),
    //         Ordering::Greater => println!("Too big!"),
    //         Ordering::Equal => {
    //             println!("You win!");
    //             break;
    //         }
    //     }
    // }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn datomic_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello, m)?)?;

    Ok(())
}
