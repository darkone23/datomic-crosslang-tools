#[path = "lib.rs"]
mod lib;

use j4rs::{ClasspathEntry, Instance, InvocationArg, Jvm, JvmBuilder};

fn main() {
    Jvm::copy_j4rs_libs_under("/tmp/datomic-crosslang-tools").expect("copied the deps");

    println!("Hello, world!");
    lib::hello();
}
