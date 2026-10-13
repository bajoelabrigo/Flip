# Retouch thumbnails

The tiles of Video > Retouch. Each one is the same portrait with that retouch applied by Flip
Studio itself (face_retouch and the face_* effects, rendered headless with the face scan on),
cropped to the face and scaled to 160 px, so a tile shows what its button really does.

Photo: "Smiling Woman Wearing Pink Off-shoulder Shirt" by Joshua McKnight, published on Pexels
and on Wikimedia Commons (File:Smiling_woman_pink_shirt_(cropped).jpg) under **CC0 1.0**
(public domain dedication). No attribution is required; it is credited here anyway.

To regenerate: run the calls from `tools/e2e` against a build with the face extras staged,
`capture` each look full-size, and crop the face. The values used are stronger than the presets
so the change reads at thumbnail size.
