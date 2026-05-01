# Initial Migration Plan

## 1. Video Web Annotator

Target folder: `tools/video-web-annotator/`

Status: migrated from `/Users/xiaoran/Desktop/code/B-Gait/B_8Fall_Demo`.

Notes:

- Copied only the current manual web annotator package.
- Excluded `legacy_pose_auto/`, bytecode caches, and generated media.
- Kept the package name `B_8Fall_Demo` so existing relative imports continue to
  resolve when commands are run from `tools/video-web-annotator/`.
- Documented launch commands in `tools/video-web-annotator/README.md`.

## 2. B_8Fall_Demo Metadata

Target folder: `datasets/b-8fall-demo/metadata/`

Status: annotation JSON files copied into
`datasets/b-8fall-demo/metadata/annotations/`.

Remaining suggested steps:

1. Add manifests describing available videos and sample identifiers.
2. Add schema documents for annotation and manifest fields.
3. Add split files only when the construction rule is documented.

## 3. External Research Code

Target folder: `external/README.md`

Current references:

- https://github.com/xiaoran007/B-MCFD
- https://github.com/xiaoran007/Kinetics-i3d-for-modern-pytorch
- https://github.com/C-H-Chien/multi_cam_jetson/pull/2

Keep these as links unless there is a clear reason to vendor code, create a
submodule, or extract a small reusable component.
