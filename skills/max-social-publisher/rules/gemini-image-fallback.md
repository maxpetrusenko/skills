# Gemini Image Fallback

## Default Rule

Do not generate an image if the post already has a strong real asset:

- demo video
- live product URL
- repo URL
- existing screenshot

Only use fallback image generation when:

- no strong media is attached, or
- the user explicitly asks for a promo image

## Provider Rule

Use Google's official image generation endpoints through the Gemini API ecosystem.

Preferred fallback model:

- `imagen-4.0-fast-generate-001`

Treat this as the default practical fallback even if the user says "Gemini image generation".

## Prompt Rule

Generate assets that feel like product proof, not generic AI art.

Good prompt ingredients:

- product category
- one concrete UI or workflow element
- clear visual composition
- no random fantasy imagery
- modern product-marketing feel

## Publish Rule

If an image is generated:

1. save locally
2. upload to Late via presign flow
3. attach as `mediaItems`

Return the generated image path and final public media URL in the summary.
