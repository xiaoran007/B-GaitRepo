# Initial Migration Plan

## 1. Video Web Annotator

Target folder: `tools/video-web-annotator/`

Suggested migration steps:

1. Identify the minimal reusable annotator files from
   `/Users/xiaoran/Desktop/code/B-Gait/B_8Fall_Demo`.
2. Move only app source, config examples, and documentation into this repo.
3. Keep large videos and exported annotation products outside the tool folder.
4. Document runtime dependencies and launch commands.

## 2. B_8Fall_Demo Metadata

Target folder: `datasets/b-8fall-demo/metadata/`

Suggested migration steps:

1. Export annotation tables from the current annotator or source repository.
2. Add manifests describing available videos and sample identifiers.
3. Add schema documents for annotation and manifest fields.
4. Add split files only when the construction rule is documented.

## 3. External Research Code

Target folder: `external/README.md`

Current references:

- https://github.com/xiaoran007/B-MCFD
- https://github.com/xiaoran007/Kinetics-i3d-for-modern-pytorch
- https://github.com/C-H-Chien/multi_cam_jetson/pull/2

Keep these as links unless there is a clear reason to vendor code, create a
submodule, or extract a small reusable component.
