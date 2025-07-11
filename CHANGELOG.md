# Changelog

## [0.3.0](https://github.com/exalsius/exalsius-cli/compare/v0.2.0...v0.3.0) (2025-07-11)


### Features

* add boilerplate for workspaces implementation ([da1885e](https://github.com/exalsius/exalsius-cli/commit/da1885eaeee18a6679639bc7f410e448a238e4f9))
* add boilerplate to get workspace elem ([056c60d](https://github.com/exalsius/exalsius-cli/commit/056c60dd18ce2fdd65232abf31f17fd024c520c5))
* add cluster operations ([4ec7bc5](https://github.com/exalsius/exalsius-cli/commit/4ec7bc519b1c2ad91a5d99e432ec9ea0409394e7))
* add node cli commands and operations ([3651b78](https://github.com/exalsius/exalsius-cli/commit/3651b78301b2aeebbc0e0fac5635e76013933dd4))
* cluster default ID support for  show-available-resources and get ([ae9ebdf](https://github.com/exalsius/exalsius-cli/commit/ae9ebdf1416f83fc7931f8d689b4794cdae605c8))
* Define a password for a jupyter notebook and wait until running ([971f488](https://github.com/exalsius/exalsius-cli/commit/971f488167b1af22b6914429e8a27191561129c8))
* display workspace access info ([#33](https://github.com/exalsius/exalsius-cli/issues/33)) ([cf5ece6](https://github.com/exalsius/exalsius-cli/commit/cf5ece6be645cc4dc5e874f9f9e0745c6d42da31))
* Implemented add and delete for workspaces ([431119c](https://github.com/exalsius/exalsius-cli/commit/431119c7e7eef655351ee018fb10ccba9e40a861))
* implemented basic login mechanism ([#37](https://github.com/exalsius/exalsius-cli/issues/37)) ([6d77ecb](https://github.com/exalsius/exalsius-cli/commit/6d77ecb7efd429068df3c4f5ad7425ac7a266257))
* Implemented CLI config management and added a configuration for default cluster setting. ([2e15b97](https://github.com/exalsius/exalsius-cli/commit/2e15b97f9a2cdd3794c3f530a5d47bbf4640ab23))
* Implemented commmands for setting and getting default cluster ([086368b](https://github.com/exalsius/exalsius-cli/commit/086368b01655cc0a2c9374d0bf5eb944de566d71))
* Implemented list workspaces and describe workspaces ([1aa0b1a](https://github.com/exalsius/exalsius-cli/commit/1aa0b1a91200d6c4920affed96b001afc35f281e))
* Implemented showing available resources for a cluster ([ca4391e](https://github.com/exalsius/exalsius-cli/commit/ca4391e73119046deb29f66c348a7195922c2f05))
* implemented workspace type options ([#41](https://github.com/exalsius/exalsius-cli/issues/41)) ([0f05618](https://github.com/exalsius/exalsius-cli/commit/0f056180e8625c4c5648b5186a9a7745fd2fb804))
* removed vscode config from tracked files. Added ides to gitignore ([#34](https://github.com/exalsius/exalsius-cli/issues/34)) ([3a00544](https://github.com/exalsius/exalsius-cli/commit/3a00544af73769dc0f38e350c70cad8ac6f926a7))
* use exalsius-api instead of skypilot api for the scan-prices command ([ccdb23c](https://github.com/exalsius/exalsius-cli/commit/ccdb23c1e327a065da5843b5d55fed9736a30f0c))


### Bug Fixes

* add ExalsiusError to ssh key operations ([8776633](https://github.com/exalsius/exalsius-cli/commit/877663320ee26060eeb5ca0faf5aa77c604d8607))
* display message when workspaces are deleted ([#35](https://github.com/exalsius/exalsius-cli/issues/35)) ([61c132a](https://github.com/exalsius/exalsius-cli/commit/61c132a9412b7d0e436f391ebab070fd3239cf5d))
* Fixed get command indent ([5cfd01b](https://github.com/exalsius/exalsius-cli/commit/5cfd01bdf8fab35063a90efb3d0163e0699b443b))
* Fixed json display of single workspace ([#31](https://github.com/exalsius/exalsius-cli/issues/31)) ([1cb7d92](https://github.com/exalsius/exalsius-cli/commit/1cb7d92439c92883d1801c5a13c7c3a59b28e52a))
* hotfixed resource definition for workspace ([#44](https://github.com/exalsius/exalsius-cli/issues/44)) ([728f358](https://github.com/exalsius/exalsius-cli/commit/728f358221a3777e3dbb5566d326f7ac6fece768))
* improved robustness of workload result printing ([#32](https://github.com/exalsius/exalsius-cli/issues/32)) ([c2b7f21](https://github.com/exalsius/exalsius-cli/commit/c2b7f211bf888b4707093a7cf6c43a605510fced))
* make cluster ID display robust ([#40](https://github.com/exalsius/exalsius-cli/issues/40)) ([f67df5e](https://github.com/exalsius/exalsius-cli/commit/f67df5e6db28b87b5a7e3e812a3ca13dba9ca54f))
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
