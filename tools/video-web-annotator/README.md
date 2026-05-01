# Video Web Annotator

Migration target: `/Users/xiaoran/Desktop/code/B-Gait/B_8Fall_Demo`.

This folder is reserved for the video web annotation tool used by
`B_8Fall_Demo`. The goal is to keep the annotator as a reusable lab utility
while separating it from dataset-specific raw media.

## Planned Contents

```text
tools/video-web-annotator/
├── README.md
├── app/ or src/          # Web app source after migration
├── config/               # Example annotation/task configs
├── examples/             # Tiny demo inputs, no large videos
└── docs/                 # UI workflow and export format notes
```

## Migration Notes

- Keep reusable annotation UI logic here.
- Keep B_8Fall_Demo-specific exported metadata under
  `datasets/b-8fall-demo/metadata/`.
- Do not commit large videos or frame dumps.
- Document any required browser, Node, Python, or backend runtime before adding
  setup commands.
