"""
Motion Capture Tools

Provides MCP tools for motion capture data import and processing.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic Models ============

class MocapImportInput(BaseModel):
    """Import mocap data"""
    filepath: str = Field(..., description="Mocap file path (.bvh, .fbx)")
    target_armature: Optional[str] = Field(None, description="Target armature name")
    scale: float = Field(1.0, description="Scale factor")
    frame_start: int = Field(1, description="Start frame")
    use_fps_scale: bool = Field(False, description="Use FPS scaling")


class MocapRetargetInput(BaseModel):
    """Retarget motion"""
    source_armature: str = Field(..., description="Source armature name")
    target_armature: str = Field(..., description="Target armature name")
    bone_mapping: Optional[Dict[str, str]] = Field(None, description="Bone mapping")


class MocapCleanInput(BaseModel):
    """Clean motion data"""
    armature_name: str = Field(..., description="Armature name")
    action_name: Optional[str] = Field(None, description="Action name")
    threshold: float = Field(0.001, description="Cleanup threshold")
    remove_noise: bool = Field(True, description="Remove noise")


class MocapBlendInput(BaseModel):
    """Blend motions"""
    armature_name: str = Field(..., description="Armature name")
    action1: str = Field(..., description="Action 1 name")
    action2: str = Field(..., description="Action 2 name")
    blend_factor: float = Field(0.5, description="Blend factor (0-1)")
    output_name: str = Field("BlendedAction", description="Output action name")


class MocapBakeInput(BaseModel):
    """Bake motion"""
    armature_name: str = Field(..., description="Armature name")
    frame_start: int = Field(1, description="Start frame")
    frame_end: int = Field(250, description="End frame")
    only_selected: bool = Field(False, description="Only bake selected bones")
    visual_keying: bool = Field(True, description="Visual keying")


# ============ Tool Registration ============

def register_mocap_tools(mcp: FastMCP, server):
    """Register motion capture tools"""

    @mcp.tool()
    async def blender_mocap_import(
        filepath: str,
        target_armature: Optional[str] = None,
        scale: float = 1.0,
        frame_start: int = 1,
        use_fps_scale: bool = False
    ) -> Dict[str, Any]:
        """
        Import motion capture data

        Args:
            filepath: Mocap file path (.bvh, .fbx)
            target_armature: Target armature name
            scale: Scale factor
            frame_start: Start frame
            use_fps_scale: Use FPS scaling
        """
        params = MocapImportInput(
            filepath=filepath,
            target_armature=target_armature,
            scale=scale,
            frame_start=frame_start,
            use_fps_scale=use_fps_scale
        )
        return await server.send_command("mocap", "import", params.model_dump())

    @mcp.tool()
    async def blender_mocap_retarget(
        source_armature: str,
        target_armature: str,
        bone_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Retarget motion to another armature

        Args:
            source_armature: Source armature name
            target_armature: Target armature name
            bone_mapping: Bone name mapping dictionary
        """
        params = MocapRetargetInput(
            source_armature=source_armature,
            target_armature=target_armature,
            bone_mapping=bone_mapping
        )
        return await server.send_command("mocap", "retarget", params.model_dump())

    @mcp.tool()
    async def blender_mocap_clean(
        armature_name: str,
        action_name: Optional[str] = None,
        threshold: float = 0.001,
        remove_noise: bool = True
    ) -> Dict[str, Any]:
        """
        Clean motion data noise

        Args:
            armature_name: Armature name
            action_name: Action name (uses current action if empty)
            threshold: Cleanup threshold
            remove_noise: Remove noise
        """
        params = MocapCleanInput(
            armature_name=armature_name,
            action_name=action_name,
            threshold=threshold,
            remove_noise=remove_noise
        )
        return await server.send_command("mocap", "clean", params.model_dump())

    @mcp.tool()
    async def blender_mocap_blend(
        armature_name: str,
        action1: str,
        action2: str,
        blend_factor: float = 0.5,
        output_name: str = "BlendedAction"
    ) -> Dict[str, Any]:
        """
        Blend two motions

        Args:
            armature_name: Armature name
            action1: First action name
            action2: Second action name
            blend_factor: Blend factor (0=full action1, 1=full action2)
            output_name: Output action name
        """
        params = MocapBlendInput(
            armature_name=armature_name,
            action1=action1,
            action2=action2,
            blend_factor=blend_factor,
            output_name=output_name
        )
        return await server.send_command("mocap", "blend", params.model_dump())

    @mcp.tool()
    async def blender_mocap_bake(
        armature_name: str,
        frame_start: int = 1,
        frame_end: int = 250,
        only_selected: bool = False,
        visual_keying: bool = True
    ) -> Dict[str, Any]:
        """
        Bake motion to keyframes

        Args:
            armature_name: Armature name
            frame_start: Start frame
            frame_end: End frame
            only_selected: Only bake selected bones
            visual_keying: Use visual keying
        """
        params = MocapBakeInput(
            armature_name=armature_name,
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=only_selected,
            visual_keying=visual_keying
        )
        return await server.send_command("mocap", "bake", params.model_dump())
