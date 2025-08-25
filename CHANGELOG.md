# Changelog

## [0.3.0](https://github.com/exalsius/exalsius-cli/compare/v0.2.0...v0.3.0) (2025-08-25)


### Features

* add boilerplate for workspaces implementation ([da1885e](https://github.com/exalsius/exalsius-cli/commit/da1885eaeee18a6679639bc7f410e448a238e4f9))
* add boilerplate to get workspace elem ([056c60d](https://github.com/exalsius/exalsius-cli/commit/056c60dd18ce2fdd65232abf31f17fd024c520c5))
* add cluster operations ([4ec7bc5](https://github.com/exalsius/exalsius-cli/commit/4ec7bc519b1c2ad91a5d99e432ec9ea0409394e7))
* add node cli commands and operations ([3651b78](https://github.com/exalsius/exalsius-cli/commit/3651b78301b2aeebbc0e0fac5635e76013933dd4))
* added command to import kubeconfig and store it locally in .kube folder ([#72](https://github.com/exalsius/exalsius-cli/issues/72)) ([4437d54](https://github.com/exalsius/exalsius-cli/commit/4437d54021eb7980d4fe1d60759108bda115b3ac))
* added services commands to support interaction with the service endpoints ([#71](https://github.com/exalsius/exalsius-cli/issues/71)) ([a879f8f](https://github.com/exalsius/exalsius-cli/commit/a879f8f8fee1b72c17c172c58e30f13add1f5ab1))
* added support for default cluster labels  ([#78](https://github.com/exalsius/exalsius-cli/issues/78)) ([d0f603a](https://github.com/exalsius/exalsius-cli/commit/d0f603a4c7eb4c7d3d2c29fa9c806b5990d8a587))
* cluster default ID support for  show-available-resources and get ([ae9ebdf](https://github.com/exalsius/exalsius-cli/commit/ae9ebdf1416f83fc7931f8d689b4794cdae605c8))
* Define a password for a jupyter notebook and wait until running ([971f488](https://github.com/exalsius/exalsius-cli/commit/971f488167b1af22b6914429e8a27191561129c8))
* device code auth flow: added QR code display as alternative when browser is not available or not opened ([#53](https://github.com/exalsius/exalsius-cli/issues/53)) ([59a8dcb](https://github.com/exalsius/exalsius-cli/commit/59a8dcb0d9d3b98e460ceb327cd885fae709fe61))
* display workspace access info ([#33](https://github.com/exalsius/exalsius-cli/issues/33)) ([cf5ece6](https://github.com/exalsius/exalsius-cli/commit/cf5ece6be645cc4dc5e874f9f9e0745c6d42da31))
* huge command pattern refactor and fix basis commands ([#60](https://github.com/exalsius/exalsius-cli/issues/60)) ([93917b5](https://github.com/exalsius/exalsius-cli/commit/93917b570a0eb647d164e508da710fdb29237b39))
* Implemented add and delete for workspaces ([431119c](https://github.com/exalsius/exalsius-cli/commit/431119c7e7eef655351ee018fb10ccba9e40a861))
* implemented auth0 device control login flow ([#50](https://github.com/exalsius/exalsius-cli/issues/50)) ([894c45d](https://github.com/exalsius/exalsius-cli/commit/894c45d0cbea6848ab2d1322b6242e8782ccef4c))
* implemented auth0 logout flow. Improved UX: user feedback when running commands while not logged in ([#51](https://github.com/exalsius/exalsius-cli/issues/51)) ([85c2fd1](https://github.com/exalsius/exalsius-cli/commit/85c2fd1d28274cb7e95fef88499b731725b95764))
* implemented auto browser opening within the device code authentication flow ([#52](https://github.com/exalsius/exalsius-cli/issues/52)) ([da4d667](https://github.com/exalsius/exalsius-cli/commit/da4d667c14a9799a1dc82ea0b62aa79e4bc6124e))
* implemented basic login mechanism ([#37](https://github.com/exalsius/exalsius-cli/issues/37)) ([6d77ecb](https://github.com/exalsius/exalsius-cli/commit/6d77ecb7efd429068df3c4f5ad7425ac7a266257))
* Implemented CLI config management and added a configuration for default cluster setting. ([2e15b97](https://github.com/exalsius/exalsius-cli/commit/2e15b97f9a2cdd3794c3f530a5d47bbf4640ab23))
* implemented commands for service endpoints ([#69](https://github.com/exalsius/exalsius-cli/issues/69)) ([6368238](https://github.com/exalsius/exalsius-cli/commit/63682386ec93b213c858f59549d9553191b432df))
* Implemented commmands for setting and getting default cluster ([086368b](https://github.com/exalsius/exalsius-cli/commit/086368b01655cc0a2c9374d0bf5eb944de566d71))
* Implemented list workspaces and describe workspaces ([1aa0b1a](https://github.com/exalsius/exalsius-cli/commit/1aa0b1a91200d6c4920affed96b001afc35f281e))
* Implemented proper authentication, credential configuration handling, and improved type safety ([#48](https://github.com/exalsius/exalsius-cli/issues/48)) ([62e24c0](https://github.com/exalsius/exalsius-cli/commit/62e24c02726857ff8145d17d20bdbeb00ee7aa54))
* Implemented showing available resources for a cluster ([ca4391e](https://github.com/exalsius/exalsius-cli/commit/ca4391e73119046deb29f66c348a7195922c2f05))
* implemented workspace type options ([#41](https://github.com/exalsius/exalsius-cli/issues/41)) ([0f05618](https://github.com/exalsius/exalsius-cli/commit/0f056180e8625c4c5648b5186a9a7745fd2fb804))
* integration of llm-inference workspace ([#46](https://github.com/exalsius/exalsius-cli/issues/46)) ([09fedcd](https://github.com/exalsius/exalsius-cli/commit/09fedcdc4abb7fba491b2f1667ef77da3c282f9d))
* refactored code project structure to vertical slicing ([#58](https://github.com/exalsius/exalsius-cli/issues/58)) ([c76675b](https://github.com/exalsius/exalsius-cli/commit/c76675b9b6301569bf6aa5edb4b788bf971b2efd))
* removed vscode config from tracked files. Added ides to gitignore ([#34](https://github.com/exalsius/exalsius-cli/issues/34)) ([3a00544](https://github.com/exalsius/exalsius-cli/commit/3a00544af73769dc0f38e350c70cad8ac6f926a7))
* show help when no sub-command is specified ([#59](https://github.com/exalsius/exalsius-cli/issues/59)) ([bd93ecb](https://github.com/exalsius/exalsius-cli/commit/bd93ecbe966ecfbd36615be7b241b91bbdfebd71))
* use exalsius-api instead of skypilot api for the scan-prices command ([ccdb23c](https://github.com/exalsius/exalsius-cli/commit/ccdb23c1e327a065da5843b5d55fed9736a30f0c))


### Bug Fixes

* add ExalsiusError to ssh key operations ([8776633](https://github.com/exalsius/exalsius-cli/commit/877663320ee26060eeb5ca0faf5aa77c604d8607))
* added error handling to service calls. Fixed ssh key command namings. Added ID argument to ssh key delete. ([cfc0121](https://github.com/exalsius/exalsius-cli/commit/cfc01218d0abc227b2192e448a3d78d553f21bed))
* display message when workspaces are deleted ([#35](https://github.com/exalsius/exalsius-cli/issues/35)) ([61c132a](https://github.com/exalsius/exalsius-cli/commit/61c132a9412b7d0e436f391ebab070fd3239cf5d))
* explicitely set the deployment name of a workspace to prevent name colisions ([#75](https://github.com/exalsius/exalsius-cli/issues/75)) ([ebf7f77](https://github.com/exalsius/exalsius-cli/commit/ebf7f77f8b19bd45bd22500004dc02c4807d5c22))
* fixed bug where key path instead of key contenct was encoded and sent to api ([#65](https://github.com/exalsius/exalsius-cli/issues/65)) ([302e45e](https://github.com/exalsius/exalsius-cli/commit/302e45eba65fa0e375212cacc694958720f2762b))
* fixed double dash in service naming ([#76](https://github.com/exalsius/exalsius-cli/issues/76)) ([5522f7c](https://github.com/exalsius/exalsius-cli/commit/5522f7c8804241bc9bb1c3eadde9da2b51947d43))
* fixed general http error handling bug ([3213140](https://github.com/exalsius/exalsius-cli/commit/321314097c86f26abd07658b226400b40ca42359))
* Fixed get command indent ([5cfd01b](https://github.com/exalsius/exalsius-cli/commit/5cfd01bdf8fab35063a90efb3d0163e0699b443b))
* Fixed json display of single workspace ([#31](https://github.com/exalsius/exalsius-cli/issues/31)) ([1cb7d92](https://github.com/exalsius/exalsius-cli/commit/1cb7d92439c92883d1801c5a13c7c3a59b28e52a))
* fixed offers response typing and updated exalsius sdk version. ([#49](https://github.com/exalsius/exalsius-cli/issues/49)) ([19b2ef9](https://github.com/exalsius/exalsius-cli/commit/19b2ef9a4ff7b7846530ada48358d08864cb1f6e))
* fixed ssh delete api call. added explicit parameter passing to node import. ([514db56](https://github.com/exalsius/exalsius-cli/commit/514db569ba2d27c8e03aa931fd537edc1e4d06c8))
* fixed the correct help message display for subcommands ([#55](https://github.com/exalsius/exalsius-cli/issues/55)) ([a53e241](https://github.com/exalsius/exalsius-cli/commit/a53e241f5dcdcc560ac120ad73e56c976e9b88f3))
* fixed workspace creation to support the new templates structure. ([#73](https://github.com/exalsius/exalsius-cli/issues/73)) ([e80da5a](https://github.com/exalsius/exalsius-cli/commit/e80da5a98f83e8bfda3456c9b918b2d19a061e2e))
* hotfixed resource definition for workspace ([#44](https://github.com/exalsius/exalsius-cli/issues/44)) ([728f358](https://github.com/exalsius/exalsius-cli/commit/728f358221a3777e3dbb5566d326f7ac6fece768))
* improved node table display ([#79](https://github.com/exalsius/exalsius-cli/issues/79)) ([b32468b](https://github.com/exalsius/exalsius-cli/commit/b32468bcff47055a5800f18df109fb3df58d67b8))
* improved robustness of workload result printing ([#32](https://github.com/exalsius/exalsius-cli/issues/32)) ([c2b7f21](https://github.com/exalsius/exalsius-cli/commit/c2b7f211bf888b4707093a7cf6c43a605510fced))
* make cluster ID display robust ([#40](https://github.com/exalsius/exalsius-cli/issues/40)) ([f67df5e](https://github.com/exalsius/exalsius-cli/commit/f67df5e6db28b87b5a7e3e812a3ca13dba9ca54f))
* moved cli list service command from clusters to services ([#68](https://github.com/exalsius/exalsius-cli/issues/68)) ([6d89af3](https://github.com/exalsius/exalsius-cli/commit/6d89af3e23443c875c6d279875088fc7feb493a5))
* proper handling of empty response on token revoke against the auth0 api ([#61](https://github.com/exalsius/exalsius-cli/issues/61)) ([ee1008d](https://github.com/exalsius/exalsius-cli/commit/ee1008db5014a8d95dc3c378e73d42ff0782a253))
* rename exalsius cli app to exls ([8768942](https://github.com/exalsius/exalsius-cli/commit/8768942aa4a279c17eefa912f659b27b967d454e))


### Documentation

* adjust readme ([166f61c](https://github.com/exalsius/exalsius-cli/commit/166f61cd1dbcfaa782a7016a6bd115074c222ccc))

## [0.2.0](https://github.com/exalsius/exalsius-cli/compare/v0.1.0...v0.2.0) (2025-03-27)


### Features

* add a colonies add-node command to add nodes via SSH to a remote cluster ([fd4baa9](https://github.com/exalsius/exalsius-cli/commit/fd4baa96495e557749d9fc1a4f52cc596a654667))
* add a command to create a remote colony ([6ea973c](https://github.com/exalsius/exalsius-cli/commit/6ea973ca0967e39f1d118dfe4ef1bdb64aed48e0))
* add example colony and job files ([#14](https://github.com/exalsius/exalsius-cli/issues/14)) ([4e01a7b](https://github.com/exalsius/exalsius-cli/commit/4e01a7b8e70300a0f46a4ee354c4b1237d1e168b))


### Bug Fixes

* argument parsing for colonies add-node command ([cdb6f39](https://github.com/exalsius/exalsius-cli/commit/cdb6f393771f5576294220f2174a6fe532b67d86))

## 0.1.0 (2025-03-27)


### Features

* Add a colony create command ([#5](https://github.com/exalsius/exalsius-cli/issues/5)) ([3458af4](https://github.com/exalsius/exalsius-cli/commit/3458af41f71f6b6b0f153ef277cccad8b370ac31))
* add a function to get the AMI IDs of Ubuntu images in AWS ([#4](https://github.com/exalsius/exalsius-cli/issues/4)) ([9660a48](https://github.com/exalsius/exalsius-cli/commit/9660a4868c18e6bade57322282362d3a3b5febd8))
* Allow to directly start jobs on existing colonies ([#6](https://github.com/exalsius/exalsius-cli/issues/6)) ([ec8ee29](https://github.com/exalsius/exalsius-cli/commit/ec8ee291cca72db6eed3a9d3f8c98b0a289e305c))


### Bug Fixes

* Refactor colony creation after job submission ([#7](https://github.com/exalsius/exalsius-cli/issues/7)) ([e000c34](https://github.com/exalsius/exalsius-cli/commit/e000c344961feb90f782dd5be8c9a0f3097cc13a))
* typo in README ([5e40d65](https://github.com/exalsius/exalsius-cli/commit/5e40d65c0fa7c1ae45ca9e042771105eff23f5fd))


### Documentation

* add first README version ([d0ae206](https://github.com/exalsius/exalsius-cli/commit/d0ae206a1fb01acdbc14bec5014fcf6d704bc23e))
* add first README version ([0758859](https://github.com/exalsius/exalsius-cli/commit/075885924b31c58238be347f92163b27414013d5))
* Adjust README format ([#8](https://github.com/exalsius/exalsius-cli/issues/8)) ([23f8cf9](https://github.com/exalsius/exalsius-cli/commit/23f8cf983a2218a418d24a2a495ee1045b4440b4))
