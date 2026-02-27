let
  pkgs = import <nixpkgs> {};
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    pyqt6
    python-lsp-server
  ]);
in
pkgs.mkShell {
  packages = [
    pythonEnv
    pkgs.pyright
  ];
  shellHook = ''
    export PYTHONPATH="${pythonEnv}/${pythonEnv.sitePackages}:''${PYTHONPATH:-}"
    # Pyright читает extraPaths из pyrightconfig.json — обновляем при входе в shell
    python3 -c "
import json
path = '${pythonEnv}/${pythonEnv.sitePackages}'
try:
    with open('pyrightconfig.json') as f: config = json.load(f)
except: config = {}
paths = list(config.get('extraPaths', ['.']))
if path not in paths: paths.append(path)
config['extraPaths'] = paths
with open('pyrightconfig.json', 'w') as f: json.dump(config, f, indent=2)
"
  '';
}

