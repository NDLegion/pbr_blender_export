# Simple PBR Exporter (Blender Add-on)

A lightweight Blender add-on for baking and exporting **PBR textures**  
(**BaseColor, Normal, Roughness, Metallic**) from **Principled BSDF** materials.

The add-on is designed to be minimal, predictable, and technically correct,  
without relying on external tools or complex material setups.

---

## ✨ Features

- Bakes **PBR textures** directly from Principled BSDF
- Outputs **PNG** textures:
  - BaseColor (RGB)
  - Normal (RGB)
  - Roughness (Grayscale)
  - Metallic (Grayscale)
- Automatically switches render engine to **Cycles**
- Works with **multiple material slots**
- No lighting baked into BaseColor

---

## 📦 Exported Textures

For an object named `MyMesh`, the following files are generated:

`export/`<br>
`└── MyMesh/`<br>
`├── MyMesh_BaseColor.png`<br>
`├── MyMesh_Normal.png`<br>
`├── MyMesh_Roughness.png`<br>
`└── MyMesh_Metallic.png`

---

## ⚙️ Requirements

### Blender
- **Blender 4.x / 5.x**
- Render Engine: **Cycles** (mandatory)

### Material
- Must use **Principled BSDF**
- Roughness and Metallic must be set on the Principled node
- Textures connected to Base Color are supported

### Object
- Must be a **Mesh**
- Must be **selected and active**
- Must have **at least one material**

### UVs (VERY IMPORTANT)
- Object **must be unwrapped**
- UVs must be inside the **0–1 UV space**
- If UVs occupy only a small area of the UV square, the baked texture will also
  only fill that area (this is expected Blender behavior)

---

## 🧠 Important Technical Notes (Nuances)

### 🔴 Cycles is REQUIRED
This add-on relies on Blender’s **Cycles baking system**.

If the render engine is set to **Eevee**:
- BaseColor may appear black or grayscale
- Roughness and Metallic may bake as black
- Normal maps may be incorrect

The add-on automatically switches the render engine to **Cycles**,  
but this behavior is intentional and required.

---

### 🎯 Active Object Requirement
Blender’s baking system only works on the **active object**.

If:
- No object is selected
- The active object is not a mesh

➡️ The export will fail.

---

### 🗺️ UV Coverage and Texture Size
Baking writes data **only where UVs exist**.

If your baked texture:
- Does not fill the entire image
- Has empty or black areas

➡️ This means your UVs do not cover the full 0–1 UV space.

This is **not a bug**.

To fix:
- Open **UV Editor**
- Scale and pack UVs to fill the UV square
- Or use `UV → Pack Islands`

---

### 🎨 BaseColor Bake Behavior
- BaseColor is baked using **Diffuse → Color only**
- No direct or indirect lighting is baked
- Result is a **pure albedo texture**

This makes it suitable for real-time engines like Roblox.

---

### 🧪 Roughness & Metallic Baking
- Roughness and Metallic are baked via a temporary **Emission node**
- Values are read directly from Principled BSDF inputs
- Output is grayscale PNG

If a map is fully black:
- The value in the material is likely `0.0`
- This is technically correct behavior

---

### 🟣 Normal Maps
- Normal maps are baked in **RGB**
- Purple / magenta colors are expected
- Output is compatible with Roblox
- (Y-flip is not applied by default)

---

## 🚀 How to Use

1. Install the add-on in Blender
2. Select a **mesh object**
3. Ensure:
   - Material uses Principled BSDF
   - Object is properly UV unwrapped
4. Switch to **Render Properties**
5. Open **Simple PBR Exporter for Roblox**
6. Set texture resolution
7. Click **Export**

---

## 🛠 Troubleshooting

### Textures are black or grayscale
- Render engine is not Cycles
- Object is not active
- Material does not use Principled BSDF

### Texture does not fill the entire image
- UVs do not fill the 0–1 UV space
- This is expected behavior

### Metallic / Roughness is fully black
- The value in the material is 0.0
- This is correct, not a bug

---

## 📄 License

Free to use, modify, and redistribute.

---

## 🤝 Contributions

Issues and pull requests are welcome.  
This add-on is intentionally minimal — simplicity is a feature.
