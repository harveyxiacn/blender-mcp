# Blender MCP Tutorials

## Introduction

These tutorials guide you through common workflows using Blender MCP. Each tutorial assumes you have completed the [Quick Start](./QUICKSTART.md) and have a working MCP connection.

---

## Tutorial 1: Your First 3D Scene

### Goal
Create a simple scene with a table, a sphere on top, and proper lighting.

### Steps

1. **Clear the scene**
```
Delete all default objects in the Blender scene
```

2. **Create the table top**
```
Create a cube named "TableTop" at position (0, 0, 0.8), scale it to (2, 1, 0.05)
```

3. **Create table legs**
```
Create 4 cylinders for table legs:
- "Leg_FL" at (-0.9, -0.45, 0.4), scale (0.05, 0.05, 0.4)
- "Leg_FR" at (0.9, -0.45, 0.4), scale (0.05, 0.05, 0.4)
- "Leg_BL" at (-0.9, 0.45, 0.4), scale (0.05, 0.05, 0.4)
- "Leg_BR" at (0.9, 0.45, 0.4), scale (0.05, 0.05, 0.4)
```

4. **Add a sphere on the table**
```
Create a UV sphere named "Ball" at (0, 0, 1.1) with radius 0.2
```

5. **Add lighting**
```
Activate the scene_setup skill, then:
- Add a sun light at (2, -2, 5) with energy 3
- Set the world background to a light blue gradient
```

6. **Set up camera and render**
```
Position the camera at (4, -3, 3) looking at the origin, then render at 1920x1080
```

---

## Tutorial 2: Low Poly Character

### Goal
Create a simple low poly character using basic shapes and modifiers.

### Steps

1. **Activate required skills**
```
Activate the "modeling" skill for mesh editing and modifiers
```

2. **Create the body**
```
Create a cube named "Body" at (0, 0, 1.2), scale to (0.4, 0.25, 0.5)
Add a Subdivision Surface modifier with level 1
```

3. **Create the head**
```
Create a UV sphere named "Head" at (0, 0, 2.0) with segments=8, rings=6 for low poly look
```

4. **Create arms and legs**
```
Create cylinders for limbs with low vertex count (vertices=6):
- "Arm_L" at (-0.55, 0, 1.3), scale (0.08, 0.08, 0.3)
- "Arm_R" at (0.55, 0, 1.3), scale (0.08, 0.08, 0.3)
- "Leg_L" at (-0.15, 0, 0.4), scale (0.1, 0.1, 0.4)
- "Leg_R" at (0.15, 0, 0.4), scale (0.1, 0.1, 0.4)
```

5. **Add materials**
```
Activate the "materials" skill, then:
- Apply a skin-colored material to Head
- Apply a blue toon material to Body
- Apply a dark material to arms and legs
```

6. **Set style**
```
Activate the "style" skill and apply LOW_POLY style preset
```

---

## Tutorial 3: Procedural Materials Showcase

### Goal
Create a material showcase scene demonstrating procedural materials.

### Steps

1. **Activate skills**
```
Activate "materials" and "scene_setup" skills
```

2. **Create showcase objects**
```
Create 5 spheres in a row, spaced 2.5 units apart:
- "Metal_Sphere" at (-5, 0, 1)
- "Wood_Sphere" at (-2.5, 0, 1)
- "Stone_Sphere" at (0, 0, 1)
- "Glass_Sphere" at (2.5, 0, 1)
- "Toon_Sphere" at (5, 0, 1)
```

3. **Apply procedural materials**
```
Apply procedural materials:
- "Metal_Sphere": chrome metal
- "Wood_Sphere": oak wood
- "Stone_Sphere": marble stone
- "Glass_Sphere": clear glass
- "Toon_Sphere": red toon shader
```

4. **Add wear effects**
```
Add edge wear effect to Metal_Sphere
Add scratches to Stone_Sphere
```

5. **Set up lighting for showcase**
```
Create a 3-point lighting setup:
- Key light (area) at (3, -3, 4)
- Fill light (area) at (-3, -2, 3)  
- Rim light (point) at (0, 3, 4)
```

---

## Tutorial 4: Animation Basics

### Goal
Animate a bouncing ball with squash and stretch.

### Steps

1. **Activate animation skill**
```
Activate the "animation" skill
```

2. **Create the ball**
```
Create a UV sphere named "BouncingBall" at (0, 0, 5)
```

3. **Set up keyframes**
```
Create a bouncing animation:
- Frame 1: position (0, 0, 5), scale (1, 1, 1)
- Frame 15: position (0, 0, 0.5), scale (1.2, 1.2, 0.7)  (squash)
- Frame 30: position (0, 0, 4), scale (0.9, 0.9, 1.1)  (stretch)
- Frame 45: position (0, 0, 0.5), scale (1.1, 1.1, 0.8)
- Frame 60: position (0, 0, 3), scale (1, 1, 1)
Set scene frame range to 1-60
```

4. **Add a ground plane**
```
Create a plane named "Ground" at (0, 0, 0), scale (5, 5, 1)
```

---

## Tutorial 5: Using the Skill System

### Goal
Learn how to efficiently use the Skill system for complex projects.

### Workflow

1. **Start by listing skills**
```
List all available skills
```

2. **Activate only what you need**
```
For a modeling task: activate_skill("modeling")
For materials: activate_skill("materials")
```

3. **Check active skills**
```
List skills to see which are active and how many tools are loaded
```

4. **Deactivate when done**
```
When finished with modeling: deactivate_skill("modeling")
This frees up context for other tasks
```

5. **Switch between tasks**
```
deactivate_skill("modeling")
activate_skill("animation")
Now work on animations with a fresh tool set
```

### Tips

- **Don't load everything at once** — activate skills as needed
- **Deactivate before switching** — free context for better AI performance
- **Use workflow guides** — each skill activation returns usage tips
- **Core tools are always available** — scene, object, utility, export
- **`blender_execute_python` is always available** — use it as a fallback for any Blender operation

---

## Next Steps

- [API Reference](./API_REFERENCE.md) — Complete tool parameter documentation
- [Architecture](./ARCHITECTURE.md) — Understand how the system works
- [Contributing](./CONTRIBUTING.md) — Add your own tools and skills
