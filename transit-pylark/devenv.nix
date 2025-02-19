{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/basics/
  env.GREET = "devenv";

  # https://devenv.sh/packages/
  packages = [
    pkgs.git
    pkgs.black
    pkgs.pipx
    (pkgs.poetry.override { python3 = pkgs.python311; })
    pkgs.python3Packages.python-lsp-server
  ];

  # https://devenv.sh/languages/
  languages.python.enable = true;
  languages.python.package = pkgs.python311;

  # https://devenv.sh/processes/
  # processes.cargo-watch.exec = "cargo-watch";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  scripts.hello.exec = ''
    echo hello from $GREET
  '';

  enterShell = ''
    hello
    git --version
  '';

  scripts.run-test-suite.exec = ''
    $HOME/.local/bin/poe test
  '';

  # https://devenv.sh/tasks/
  tasks = {
    "transit:setup".exec = "pipx install poethepoet && ${pkgs.poetry}/bin/poetry install";
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
    "devenv:enterShell".after = [ "transit:setup" ];
  };

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
