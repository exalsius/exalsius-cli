# Changelog

## [0.3.0](https://github.com/exalsius/exalsius-cli/compare/v0.2.0...v0.3.0) (2026-02-08)


### Features

* adapted from DiLoCo naming to to multinode-training naming. Removed user prompt for node role when creating cluster. Set cluster type to remote and removed user prompt for cluster type. ([c85472c](https://github.com/exalsius/exalsius-cli/commit/c85472c05ae3ed40effbbcca492106139435a524))
* add boilerplate for workspaces implementation ([da1885e](https://github.com/exalsius/exalsius-cli/commit/da1885eaeee18a6679639bc7f410e448a238e4f9))
* add boilerplate to get workspace elem ([056c60d](https://github.com/exalsius/exalsius-cli/commit/056c60dd18ce2fdd65232abf31f17fd024c520c5))
* add cluster operations ([4ec7bc5](https://github.com/exalsius/exalsius-cli/commit/4ec7bc519b1c2ad91a5d99e432ec9ea0409394e7))
* add node cli commands and operations ([3651b78](https://github.com/exalsius/exalsius-cli/commit/3651b78301b2aeebbc0e0fac5635e76013933dd4))
* add option to prepare llm inference env ([#175](https://github.com/exalsius/exalsius-cli/issues/175)) ([db47ed9](https://github.com/exalsius/exalsius-cli/commit/db47ed9b1f95116c6f24d8187dde0d69550b048d))
* add possibility to request scoped tokens for agent node(s) ([#89](https://github.com/exalsius/exalsius-cli/issues/89)) ([ea79167](https://github.com/exalsius/exalsius-cli/commit/ea79167fa2e43fab5de1c3cd99fa71db7844fd93))
* add pyright to precommit and ci ([#91](https://github.com/exalsius/exalsius-cli/issues/91)) ([9f39e71](https://github.com/exalsius/exalsius-cli/commit/9f39e71fae2914e0a677db120ae453b4497468c6))
* added cluster list nodes flow and cluster add node flow ([#121](https://github.com/exalsius/exalsius-cli/issues/121)) ([cb52376](https://github.com/exalsius/exalsius-cli/commit/cb523768c99554a2b6ed0a78e262ac31c622b6bf))
* added command to import kubeconfig and store it locally in .kube folder ([#72](https://github.com/exalsius/exalsius-cli/issues/72)) ([4437d54](https://github.com/exalsius/exalsius-cli/commit/4437d54021eb7980d4fe1d60759108bda115b3ac))
* added diloco workspace ([#82](https://github.com/exalsius/exalsius-cli/issues/82)) ([f33e8d5](https://github.com/exalsius/exalsius-cli/commit/f33e8d5c82a739510d424ff3bef6f46f9ce581a1))
* added diloco workspace torch compile params ([#97](https://github.com/exalsius/exalsius-cli/issues/97)) ([8c070c2](https://github.com/exalsius/exalsius-cli/commit/8c070c262bd220d1b2ba24435e27ce74f824d99b))
* added elastic auto-configuration and improved workspace display summary ([#127](https://github.com/exalsius/exalsius-cli/issues/127)) ([b67dda8](https://github.com/exalsius/exalsius-cli/commit/b67dda8bd2d2e572a947240009fc28353b941940))
* added interactive cluster selection if no cluster id is provided for a workspace deployment ([#130](https://github.com/exalsius/exalsius-cli/issues/130)) ([b288412](https://github.com/exalsius/exalsius-cli/commit/b28841251964af58fbb6db121b845f323476cc58))
* added marimo workspace and fixed docker image defaults ([#95](https://github.com/exalsius/exalsius-cli/issues/95)) ([698e0d9](https://github.com/exalsius/exalsius-cli/commit/698e0d91a9f13fbd9a72b574762fc7a8cabb3cfe))
* added node import loop into interactive mode ([#118](https://github.com/exalsius/exalsius-cli/issues/118)) ([05ad459](https://github.com/exalsius/exalsius-cli/commit/05ad45932cfe341e2fbba1112f569b4a18820b0c))
* added services commands to support interaction with the service endpoints ([#71](https://github.com/exalsius/exalsius-cli/issues/71)) ([a879f8f](https://github.com/exalsius/exalsius-cli/commit/a879f8f8fee1b72c17c172c58e30f13add1f5ab1))
* added support for default cluster labels  ([#78](https://github.com/exalsius/exalsius-cli/issues/78)) ([d0f603a](https://github.com/exalsius/exalsius-cli/commit/d0f603a4c7eb4c7d3d2c29fa9c806b5990d8a587))
* added text validation argument for user text queries ([6f08573](https://github.com/exalsius/exalsius-cli/commit/6f085739cf020cf65a82d614ac66ed190a8df09a))
* allow to specify resources by name and id ([cf17eeb](https://github.com/exalsius/exalsius-cli/commit/cf17eeb238b303e339ea24279e14f38f376536f4))
* cluster default ID support for  show-available-resources and get ([ae9ebdf](https://github.com/exalsius/exalsius-cli/commit/ae9ebdf1416f83fc7931f8d689b4794cdae605c8))
* **clusters:** add subcommand to get monitoring dashboard url ([da380b5](https://github.com/exalsius/exalsius-cli/commit/da380b5915baa84a49c11fe652a835e0e44759ad))
* configuration option for deploying observability into cluster ([#80](https://github.com/exalsius/exalsius-cli/issues/80)) ([da6c564](https://github.com/exalsius/exalsius-cli/commit/da6c564ba73887e8e61b16ed159ab40d2437c6b7))
* Define a password for a jupyter notebook and wait until running ([971f488](https://github.com/exalsius/exalsius-cli/commit/971f488167b1af22b6914429e8a27191561129c8))
* device code auth flow: added QR code display as alternative when browser is not available or not opened ([#53](https://github.com/exalsius/exalsius-cli/issues/53)) ([59a8dcb](https://github.com/exalsius/exalsius-cli/commit/59a8dcb0d9d3b98e460ceb327cd885fae709fe61))
* display workspace access info ([#33](https://github.com/exalsius/exalsius-cli/issues/33)) ([cf5ece6](https://github.com/exalsius/exalsius-cli/commit/cf5ece6be645cc4dc5e874f9f9e0745c6d42da31))
* hexagonal architecture migration & core refactoring ([#125](https://github.com/exalsius/exalsius-cli/issues/125)) ([2e8c000](https://github.com/exalsius/exalsius-cli/commit/2e8c000a3ade51f9de56d8d6a9840826538363f6))
* huge command pattern refactor and fix basis commands ([#60](https://github.com/exalsius/exalsius-cli/issues/60)) ([93917b5](https://github.com/exalsius/exalsius-cli/commit/93917b570a0eb647d164e508da710fdb29237b39))
* huge refactor ([#99](https://github.com/exalsius/exalsius-cli/issues/99)) ([9a8753f](https://github.com/exalsius/exalsius-cli/commit/9a8753f1f740a85d2d2d35d08293ebfa5ceeead9))
* implemented a table view for the clusters nodes ([#84](https://github.com/exalsius/exalsius-cli/issues/84)) ([5c9a498](https://github.com/exalsius/exalsius-cli/commit/5c9a498f02146f48860c27641c0d5312adb2a45b))
* Implemented add and delete for workspaces ([431119c](https://github.com/exalsius/exalsius-cli/commit/431119c7e7eef655351ee018fb10ccba9e40a861))
* implemented auth0 device control login flow ([#50](https://github.com/exalsius/exalsius-cli/issues/50)) ([894c45d](https://github.com/exalsius/exalsius-cli/commit/894c45d0cbea6848ab2d1322b6242e8782ccef4c))
* implemented auth0 logout flow. Improved UX: user feedback when running commands while not logged in ([#51](https://github.com/exalsius/exalsius-cli/issues/51)) ([85c2fd1](https://github.com/exalsius/exalsius-cli/commit/85c2fd1d28274cb7e95fef88499b731725b95764))
* implemented auto browser opening within the device code authentication flow ([#52](https://github.com/exalsius/exalsius-cli/issues/52)) ([da4d667](https://github.com/exalsius/exalsius-cli/commit/da4d667c14a9799a1dc82ea0b62aa79e4bc6124e))
* implemented basic login mechanism ([#37](https://github.com/exalsius/exalsius-cli/issues/37)) ([6d77ecb](https://github.com/exalsius/exalsius-cli/commit/6d77ecb7efd429068df3c4f5ad7425ac7a266257))
* Implemented CLI config management and added a configuration for default cluster setting. ([2e15b97](https://github.com/exalsius/exalsius-cli/commit/2e15b97f9a2cdd3794c3f530a5d47bbf4640ab23))
* implemented commands for service endpoints ([#69](https://github.com/exalsius/exalsius-cli/issues/69)) ([6368238](https://github.com/exalsius/exalsius-cli/commit/63682386ec93b213c858f59549d9553191b432df))
* Implemented commmands for setting and getting default cluster ([086368b](https://github.com/exalsius/exalsius-cli/commit/086368b01655cc0a2c9374d0bf5eb944de566d71))
* Implemented list workspaces and describe workspaces ([1aa0b1a](https://github.com/exalsius/exalsius-cli/commit/1aa0b1a91200d6c4920affed96b001afc35f281e))
* implemented node removal from cluster ([#85](https://github.com/exalsius/exalsius-cli/issues/85)) ([5b597fe](https://github.com/exalsius/exalsius-cli/commit/5b597fef4aad3f4a12edd73f1522c4df00efdda7))
* Implemented proper authentication, credential configuration handling, and improved type safety ([#48](https://github.com/exalsius/exalsius-cli/issues/48)) ([62e24c0](https://github.com/exalsius/exalsius-cli/commit/62e24c02726857ff8145d17d20bdbeb00ee7aa54))
* Implemented showing available resources for a cluster ([ca4391e](https://github.com/exalsius/exalsius-cli/commit/ca4391e73119046deb29f66c348a7195922c2f05))
* implemented workspace type options ([#41](https://github.com/exalsius/exalsius-cli/issues/41)) ([0f05618](https://github.com/exalsius/exalsius-cli/commit/0f056180e8625c4c5648b5186a9a7745fd2fb804))
* improve node import robustness and show self-managed nodes infos ([#132](https://github.com/exalsius/exalsius-cli/issues/132)) ([b8f4204](https://github.com/exalsius/exalsius-cli/commit/b8f42049edeea6301a14b5b929ee3a9119f6e78c))
* improve user interrupt exception handling during flow ([ccffd1c](https://github.com/exalsius/exalsius-cli/commit/ccffd1c83b7b1e2e1b83be44fc6ae00f71ef4b40))
* improve workspace robustness ([#144](https://github.com/exalsius/exalsius-cli/issues/144)) ([6cb52c9](https://github.com/exalsius/exalsius-cli/commit/6cb52c9e954d278eff2c60130a7bf7b268f38262))
* improved clusters management robustness. improved command error display. fixed remove nodes from cluster. ([#134](https://github.com/exalsius/exalsius-cli/issues/134)) ([2c3ba0e](https://github.com/exalsius/exalsius-cli/commit/2c3ba0e265a11e8cae88edad2808eb3e1528faec))
* improved nodes delete command to support deletion of multiple nodes ([#138](https://github.com/exalsius/exalsius-cli/issues/138)) ([402c273](https://github.com/exalsius/exalsius-cli/commit/402c273687ef4fd264d34d818be8e3e3b5e6cbc0))
* improved robustness of diloco workspace ([#148](https://github.com/exalsius/exalsius-cli/issues/148)) ([e29cc66](https://github.com/exalsius/exalsius-cli/commit/e29cc66c2f457d0352304a8607f2090357fb6e3e))
* integrated interactive flow for cluster creation ([524018b](https://github.com/exalsius/exalsius-cli/commit/524018b1ace8764ea7de3a7c9242777c408481ea))
* integration of llm-inference workspace ([#46](https://github.com/exalsius/exalsius-cli/issues/46)) ([09fedcd](https://github.com/exalsius/exalsius-cli/commit/09fedcdc4abb7fba491b2f1667ef77da3c282f9d))
* interactive workflow for template-based workspace deployment ([#119](https://github.com/exalsius/exalsius-cli/issues/119)) ([0aad4d7](https://github.com/exalsius/exalsius-cli/commit/0aad4d7e853b08e4c9f3515b6e350f9910ff001a))
* list workspaces shows all workspaces from all clusters if no cluster id is provided ([#131](https://github.com/exalsius/exalsius-cli/issues/131)) ([b057935](https://github.com/exalsius/exalsius-cli/commit/b0579351bcc049cf287e84a2061d375f925988bc))
* modular and reusable display and rendering architecture ([#94](https://github.com/exalsius/exalsius-cli/issues/94)) ([da2525a](https://github.com/exalsius/exalsius-cli/commit/da2525a5748383bf66d8142565cce5db66a69daf))
* **nodes:** implement interactive node import workflow ([2db71e9](https://github.com/exalsius/exalsius-cli/commit/2db71e99f85e727d485e62f66fd82acbadd69290))
* re-enable telemetry CLI flag; hide vpn CLI flag ([#174](https://github.com/exalsius/exalsius-cli/issues/174)) ([57f583d](https://github.com/exalsius/exalsius-cli/commit/57f583d691220f53240d45ad8af97a602b4f4115))
* refactored code project structure to vertical slicing ([#58](https://github.com/exalsius/exalsius-cli/issues/58)) ([c76675b](https://github.com/exalsius/exalsius-cli/commit/c76675b9b6301569bf6aa5edb4b788bf971b2efd))
* refactored workspace code structure ([#88](https://github.com/exalsius/exalsius-cli/issues/88)) ([70097dc](https://github.com/exalsius/exalsius-cli/commit/70097dcdeb8f051e5696f9eacea255af9bea9147))
* remove validator default in deep commons implementation ([2587302](https://github.com/exalsius/exalsius-cli/commit/25873026a07c4d7db457427d5f5a507ba1b4527c))
* removed vscode config from tracked files. Added ides to gitignore ([#34](https://github.com/exalsius/exalsius-cli/issues/34)) ([3a00544](https://github.com/exalsius/exalsius-cli/commit/3a00544af73769dc0f38e350c70cad8ac6f926a7))
* show help when no sub-command is specified ([#59](https://github.com/exalsius/exalsius-cli/issues/59)) ([bd93ecb](https://github.com/exalsius/exalsius-cli/commit/bd93ecbe966ecfbd36615be7b241b91bbdfebd71))
* show humanized timestamps in list view for resources ([4101113](https://github.com/exalsius/exalsius-cli/commit/41011139cfba5da29a4e04ed9f17bd469054db5c))
* simplified the logic of cluster creation ([#110](https://github.com/exalsius/exalsius-cli/issues/110)) ([a8f94ab](https://github.com/exalsius/exalsius-cli/commit/a8f94ab83fe3be224a55544b6434af1a22d26773))
* streamlined node import flow ([69eea1f](https://github.com/exalsius/exalsius-cli/commit/69eea1ff10e6710c9a5fc2582dd883175fa1d0b7))
* update exalsius workload cluster-labels ([#181](https://github.com/exalsius/exalsius-cli/issues/181)) ([588f8e2](https://github.com/exalsius/exalsius-cli/commit/588f8e2a3dcf47ec68ce611e9007d6fe0a1e246f))
* use exalsius-api instead of skypilot api for the scan-prices command ([ccdb23c](https://github.com/exalsius/exalsius-cli/commit/ccdb23c1e327a065da5843b5d55fed9736a30f0c))
* workspace configurator validation supports nested variable dict validation ([#126](https://github.com/exalsius/exalsius-cli/issues/126)) ([28a30ad](https://github.com/exalsius/exalsius-cli/commit/28a30adb24843c78747dbf71751d6cc65ed3b1aa))


### Bug Fixes

* adapt tests ([#93](https://github.com/exalsius/exalsius-cli/issues/93)) ([947b98c](https://github.com/exalsius/exalsius-cli/commit/947b98caedb764226343d5f6420e79504987a018))
* add an option for setting a password for the marimo workspace ([#96](https://github.com/exalsius/exalsius-cli/issues/96)) ([58fd646](https://github.com/exalsius/exalsius-cli/commit/58fd646c280884bea17fab2b156d01d3cc434fd0))
* add ExalsiusError to ssh key operations ([8776633](https://github.com/exalsius/exalsius-cli/commit/877663320ee26060eeb5ca0faf5aa77c604d8607))
* added error handling to service calls. Fixed ssh key command namings. Added ID argument to ssh key delete. ([cfc0121](https://github.com/exalsius/exalsius-cli/commit/cfc01218d0abc227b2192e448a3d78d553f21bed))
* auth leeway config ([#120](https://github.com/exalsius/exalsius-cli/issues/120)) ([ee8aff6](https://github.com/exalsius/exalsius-cli/commit/ee8aff6a1bc42524e765e762339f538f911501cf))
* **auth:** avoid redundant JWKS fetch on every CLI command ([#183](https://github.com/exalsius/exalsius-cli/issues/183)) ([8e97ad0](https://github.com/exalsius/exalsius-cli/commit/8e97ad087b03ce646562416225641bd871b40a04))
* **cluster-create:** convert cluster type string to upper-case ([#129](https://github.com/exalsius/exalsius-cli/issues/129)) ([540b303](https://github.com/exalsius/exalsius-cli/commit/540b303c6baace49b7d0b7ea8aedefc74e97a62a))
* **clusters:** only fetch cluster resources when status is READY ([64b9e7e](https://github.com/exalsius/exalsius-cli/commit/64b9e7e93d92592986b48b76ac7303897e2e27a4))
* **clusters:** remove docker cluster creation option since it is only used for local testing ([89b1c78](https://github.com/exalsius/exalsius-cli/commit/89b1c785cb8d3c7122c4fc388b5bbd6bbd3f3521))
* default user is ubuntu ([#123](https://github.com/exalsius/exalsius-cli/issues/123)) ([f898011](https://github.com/exalsius/exalsius-cli/commit/f898011e8e73099626acbe096745c42517ae8ef6))
* dependency cleanup ([#92](https://github.com/exalsius/exalsius-cli/issues/92)) ([501275a](https://github.com/exalsius/exalsius-cli/commit/501275a77b850cdeac8126afc596d24ae6a1c546))
* disabled multi-node import in node import flow ([#154](https://github.com/exalsius/exalsius-cli/issues/154)) ([244af52](https://github.com/exalsius/exalsius-cli/commit/244af523d7dff9ab9096be2396ccdcc1bc811abc))
* disabled telemetry option for now ([#147](https://github.com/exalsius/exalsius-cli/issues/147)) ([d392da3](https://github.com/exalsius/exalsius-cli/commit/d392da3148a4888c01076c5ff87449a559c26156))
* display message when workspaces are deleted ([#35](https://github.com/exalsius/exalsius-cli/issues/35)) ([61c132a](https://github.com/exalsius/exalsius-cli/commit/61c132a9412b7d0e436f391ebab070fd3239cf5d))
* explicitely set the deployment name of a workspace to prevent name colisions ([#75](https://github.com/exalsius/exalsius-cli/issues/75)) ([ebf7f77](https://github.com/exalsius/exalsius-cli/commit/ebf7f77f8b19bd45bd22500004dc02c4807d5c22))
* fix refactor artifacts ([#108](https://github.com/exalsius/exalsius-cli/issues/108)) ([fcebe0b](https://github.com/exalsius/exalsius-cli/commit/fcebe0b36bc95014c713cd6e053aae90b06cd938))
* fix token expiry handling ([#142](https://github.com/exalsius/exalsius-cli/issues/142)) ([d0c6c9d](https://github.com/exalsius/exalsius-cli/commit/d0c6c9dce043b29d8aa55b27a0b9db03a55f86da))
* fixed auth tests and deployment token ([#90](https://github.com/exalsius/exalsius-cli/issues/90)) ([9ab8a31](https://github.com/exalsius/exalsius-cli/commit/9ab8a3142953c06a940e8bf1086b19477d705fc5))
* fixed broken workspace deployment ([#171](https://github.com/exalsius/exalsius-cli/issues/171)) ([67a6bde](https://github.com/exalsius/exalsius-cli/commit/67a6bdebb60ded2efdb54cbbc90a0b0dfa1fa363))
* fixed bug where key path instead of key contenct was encoded and sent to api ([#65](https://github.com/exalsius/exalsius-cli/issues/65)) ([302e45e](https://github.com/exalsius/exalsius-cli/commit/302e45eba65fa0e375212cacc694958720f2762b))
* fixed cluster node rendering bug ([#149](https://github.com/exalsius/exalsius-cli/issues/149)) ([e1279aa](https://github.com/exalsius/exalsius-cli/commit/e1279aae3abd56f3a5f54e032694034ea6e33778))
* fixed double dash in service naming ([#76](https://github.com/exalsius/exalsius-cli/issues/76)) ([5522f7c](https://github.com/exalsius/exalsius-cli/commit/5522f7c8804241bc9bb1c3eadde9da2b51947d43))
* fixed error display on CLI layer to catch all error types ([#140](https://github.com/exalsius/exalsius-cli/issues/140)) ([d54ed4e](https://github.com/exalsius/exalsius-cli/commit/d54ed4ec72c5061d4c0e3af35e4bf66bee45b0f8))
* fixed general http error handling bug ([3213140](https://github.com/exalsius/exalsius-cli/commit/321314097c86f26abd07658b226400b40ca42359))
* Fixed get command indent ([5cfd01b](https://github.com/exalsius/exalsius-cli/commit/5cfd01bdf8fab35063a90efb3d0163e0699b443b))
* Fixed json display of single workspace ([#31](https://github.com/exalsius/exalsius-cli/issues/31)) ([1cb7d92](https://github.com/exalsius/exalsius-cli/commit/1cb7d92439c92883d1801c5a13c7c3a59b28e52a))
* fixed layer violation of decorators and some minor fixes ([#162](https://github.com/exalsius/exalsius-cli/issues/162)) ([aac23dc](https://github.com/exalsius/exalsius-cli/commit/aac23dc0fef08db78f62aa02da3d1ab0ff8ad2d9))
* fixed node listing([#160](https://github.com/exalsius/exalsius-cli/issues/160)) ([b099bb0](https://github.com/exalsius/exalsius-cli/commit/b099bb032af7f20eecbc6e8f10caea8dcf10f99e))
* fixed offers response typing and updated exalsius sdk version. ([#49](https://github.com/exalsius/exalsius-cli/issues/49)) ([19b2ef9](https://github.com/exalsius/exalsius-cli/commit/19b2ef9a4ff7b7846530ada48358d08864cb1f6e))
* fixed ressource calculation ([#155](https://github.com/exalsius/exalsius-cli/issues/155)) ([759f58f](https://github.com/exalsius/exalsius-cli/commit/759f58f5beccf0c8861675c900c6f2646f3c78fc))
* fixed single dto table rendering ([#153](https://github.com/exalsius/exalsius-cli/issues/153)) ([dadfae9](https://github.com/exalsius/exalsius-cli/commit/dadfae93b638d5d8c6cd59b7c48b1723ad7dad1f))
* fixed ssh delete api call. added explicit parameter passing to node import. ([514db56](https://github.com/exalsius/exalsius-cli/commit/514db569ba2d27c8e03aa931fd537edc1e4d06c8))
* fixed table rendering for single item display ([#133](https://github.com/exalsius/exalsius-cli/issues/133)) ([72a9610](https://github.com/exalsius/exalsius-cli/commit/72a9610d8ed0806d4cd5b70077165d677f1d5aaf))
* fixed the correct help message display for subcommands ([#55](https://github.com/exalsius/exalsius-cli/issues/55)) ([a53e241](https://github.com/exalsius/exalsius-cli/commit/a53e241f5dcdcc560ac120ad73e56c976e9b88f3))
* fixed time zone ambiguity issue when checking for token expiry ([#136](https://github.com/exalsius/exalsius-cli/issues/136)) ([6a7c12e](https://github.com/exalsius/exalsius-cli/commit/6a7c12e6dc35bca74b451961c1f87ed9130a2e01))
* fixed workspace creation to support the new templates structure. ([#73](https://github.com/exalsius/exalsius-cli/issues/73)) ([e80da5a](https://github.com/exalsius/exalsius-cli/commit/e80da5a98f83e8bfda3456c9b918b2d19a061e2e))
* fixed workspace rendering for display ([#128](https://github.com/exalsius/exalsius-cli/issues/128)) ([51816e3](https://github.com/exalsius/exalsius-cli/commit/51816e33cd06d93c291c96e9b7354ca786f1de64))
* fixed workspaces access info ([#122](https://github.com/exalsius/exalsius-cli/issues/122)) ([350ed8f](https://github.com/exalsius/exalsius-cli/commit/350ed8f2d891061d9f08f5b605c2db5eb25cb911))
* hotfix resource calc ([#157](https://github.com/exalsius/exalsius-cli/issues/157)) ([edacce7](https://github.com/exalsius/exalsius-cli/commit/edacce71cee44ada69ace47687095a2b59492eff))
* hotfixed resource definition for workspace ([#44](https://github.com/exalsius/exalsius-cli/issues/44)) ([728f358](https://github.com/exalsius/exalsius-cli/commit/728f358221a3777e3dbb5566d326f7ac6fece768))
* improved cluster resource loading robustness ([#135](https://github.com/exalsius/exalsius-cli/issues/135)) ([ad33002](https://github.com/exalsius/exalsius-cli/commit/ad330020205c0271d8a0bfed83ed10f341a4e896))
* improved clusters domain object robustness ([#161](https://github.com/exalsius/exalsius-cli/issues/161)) ([6e5b3d9](https://github.com/exalsius/exalsius-cli/commit/6e5b3d94ff68ba9bcbc9eeddd27153d352e5d5c9))
* improved node table display ([#79](https://github.com/exalsius/exalsius-cli/issues/79)) ([b32468b](https://github.com/exalsius/exalsius-cli/commit/b32468bcff47055a5800f18df109fb3df58d67b8))
* improved robustness of workload result printing ([#32](https://github.com/exalsius/exalsius-cli/issues/32)) ([c2b7f21](https://github.com/exalsius/exalsius-cli/commit/c2b7f211bf888b4707093a7cf6c43a605510fced))
* make cluster ID display robust ([#40](https://github.com/exalsius/exalsius-cli/issues/40)) ([f67df5e](https://github.com/exalsius/exalsius-cli/commit/f67df5e6db28b87b5a7e3e812a3ca13dba9ca54f))
* **marimo, jupyter:** change duplicate -p flag to -s for storage ([36c15e0](https://github.com/exalsius/exalsius-cli/commit/36c15e0dde0ca48da1879c35166ffc0f3311acfd))
* moved cli list service command from clusters to services ([#68](https://github.com/exalsius/exalsius-cli/issues/68)) ([6d89af3](https://github.com/exalsius/exalsius-cli/commit/6d89af3e23443c875c6d279875088fc7feb493a5))
* Node import ssh key username is default empty. Show add clusters nodes as not implemented. ([#156](https://github.com/exalsius/exalsius-cli/issues/156)) ([f3a6ba3](https://github.com/exalsius/exalsius-cli/commit/f3a6ba334089f20566ed667ba7fc45aa429e96fc))
* nodes display ([#81](https://github.com/exalsius/exalsius-cli/issues/81)) ([cf736b3](https://github.com/exalsius/exalsius-cli/commit/cf736b3d231b792b72f4fa4e324f9174a8013bf3))
* **nodes:** add BaseNodesDisplayManager contract ([aac343e](https://github.com/exalsius/exalsius-cli/commit/aac343e8023f04daa6ff8b6c95014f20723b4d3c))
* **nodes:** add missing flows ([344ace6](https://github.com/exalsius/exalsius-cli/commit/344ace682c7922a5caaf4b6862ffa2e741a24d21))
* **nodes:** decouple interactive node import flow from service layer ([45df45a](https://github.com/exalsius/exalsius-cli/commit/45df45a512c0a0f48006d4a642c615eb953a0a90))
* **nodes:** do not use offers import for now! ([2168f07](https://github.com/exalsius/exalsius-cli/commit/2168f078b9ab6b85c0ecf345ba21736ff617dd1e))
* proper handling of empty response on token revoke against the auth0 api ([#61](https://github.com/exalsius/exalsius-cli/issues/61)) ([ee1008d](https://github.com/exalsius/exalsius-cli/commit/ee1008db5014a8d95dc3c378e73d42ff0782a253))
* rename exalsius cli app to exls ([8768942](https://github.com/exalsius/exalsius-cli/commit/8768942aa4a279c17eefa912f659b27b967d454e))
* renamed ci to make badge work ([797ef65](https://github.com/exalsius/exalsius-cli/commit/797ef657ef6cda6788df81272dea549d863d2c86))
* renamed ci to make badge work ([#116](https://github.com/exalsius/exalsius-cli/issues/116)) ([339bce0](https://github.com/exalsius/exalsius-cli/commit/339bce0763a425a112a9117f2ee3f88b6b4c250c))
* set gpu vendor variable when deploying a workspaces ([#146](https://github.com/exalsius/exalsius-cli/issues/146)) ([eab8ddb](https://github.com/exalsius/exalsius-cli/commit/eab8ddba1989aa77f9ec53d0a96f281589b4a12c))
* set request ressource paramters of gpu vendor and gpu type to None if not known ([#151](https://github.com/exalsius/exalsius-cli/issues/151)) ([cc2b239](https://github.com/exalsius/exalsius-cli/commit/cc2b23986f1b9b221d7fa8ddb537513d2fffc047))
* setting gpu vendor enabled variables based on GPU availability in the cluster ([#137](https://github.com/exalsius/exalsius-cli/issues/137)) ([39b732d](https://github.com/exalsius/exalsius-cli/commit/39b732d4780e0e287a4559f8c52eabe39447bd1d))
* show only available nodes when deploying a cluster ([21b7fb4](https://github.com/exalsius/exalsius-cli/commit/21b7fb41bfce508af428fd300b35036e602e3400))
* update WorkspaceAccessInformation to use external_ips list ([#152](https://github.com/exalsius/exalsius-cli/issues/152)) ([f03144b](https://github.com/exalsius/exalsius-cli/commit/f03144b72ba819be43debf7b9a710c24f62956da))
* **workspaces:** add default ssh user to devpod access information ([a225fb6](https://github.com/exalsius/exalsius-cli/commit/a225fb63bf6014fd3d2cfd51ffaaa8d32887a3ee))


### Documentation

* adjust readme ([166f61c](https://github.com/exalsius/exalsius-cli/commit/166f61cd1dbcfaa782a7016a6bd115074c222ccc))
* fixed header format in readme ([#115](https://github.com/exalsius/exalsius-cli/issues/115)) ([be78867](https://github.com/exalsius/exalsius-cli/commit/be788671c07fb8cb4fe53e4c81549d7fb94ffa1a))
* updated readme docs ([#114](https://github.com/exalsius/exalsius-cli/issues/114)) ([7d875c7](https://github.com/exalsius/exalsius-cli/commit/7d875c7538a57fd2e42eddd847587e43b9a8cc7b))

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
