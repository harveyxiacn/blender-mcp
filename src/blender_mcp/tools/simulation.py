"""
高级模拟工具

提供流体、烟雾、海洋等高级模拟的MCP工具。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


# ============ Pydantic 模型 ============

class FluidDomainInput(BaseModel):
    """流体域设置"""
    object_name: str = Field(..., description="对象名称")
    domain_type: str = Field("LIQUID", description="域类型: LIQUID, GAS")
    resolution: int = Field(64, description="分辨率")
    use_adaptive_domain: bool = Field(False, description="自适应域")


class FluidFlowInput(BaseModel):
    """流体流入/流出"""
    object_name: str = Field(..., description="对象名称")
    flow_type: str = Field("INFLOW", description="类型: INFLOW, OUTFLOW, GEOMETRY")
    flow_behavior: str = Field("GEOMETRY", description="行为: INFLOW, OUTFLOW, GEOMETRY")
    use_initial_velocity: bool = Field(False, description="使用初始速度")
    velocity: List[float] = Field([0, 0, 0], description="速度 [x, y, z]")


class FluidEffectorInput(BaseModel):
    """流体效果器"""
    object_name: str = Field(..., description="对象名称")
    effector_type: str = Field("COLLISION", description="类型: COLLISION, GUIDE")


class SmokeDomainInput(BaseModel):
    """烟雾/火焰域"""
    object_name: str = Field(..., description="对象名称")
    smoke_type: str = Field("SMOKE", description="类型: SMOKE, FIRE, BOTH")
    resolution: int = Field(32, description="分辨率")
    use_high_resolution: bool = Field(False, description="高分辨率")


class SmokeFlowInput(BaseModel):
    """烟雾流入"""
    object_name: str = Field(..., description="对象名称")
    flow_type: str = Field("SMOKE", description="类型: SMOKE, FIRE, BOTH")
    temperature: float = Field(1.0, description="温度")
    density: float = Field(1.0, description="密度")
    smoke_color: List[float] = Field([1, 1, 1], description="烟雾颜色")


class OceanModifierInput(BaseModel):
    """海洋修改器"""
    object_name: str = Field(..., description="对象名称")
    resolution: int = Field(7, description="分辨率 (2^n)")
    spatial_size: int = Field(50, description="空间大小")
    wave_scale: float = Field(1.0, description="波浪缩放")
    choppiness: float = Field(1.0, description="波涛汹涌度")
    wind_velocity: float = Field(30.0, description="风速")
    use_foam: bool = Field(False, description="使用泡沫")


class DynamicPaintCanvasInput(BaseModel):
    """动态绘制画布"""
    object_name: str = Field(..., description="对象名称")
    surface_type: str = Field("PAINT", description="类型: PAINT, DISPLACE, WAVE, WEIGHT")
    use_dissolve: bool = Field(False, description="使用溶解")
    dissolve_speed: int = Field(80, description="溶解速度")


class DynamicPaintBrushInput(BaseModel):
    """动态绘制笔刷"""
    object_name: str = Field(..., description="对象名称")
    paint_color: List[float] = Field([1, 0, 0], description="绘制颜色")
    paint_alpha: float = Field(1.0, description="透明度")


class SimulationBakeInput(BaseModel):
    """烘焙模拟"""
    object_name: str = Field(..., description="域对象名称")
    frame_start: int = Field(1, description="开始帧")
    frame_end: int = Field(250, description="结束帧")


# ============ 工具注册 ============

def register_simulation_tools(mcp: FastMCP, server):
    """注册高级模拟工具"""
    
    @mcp.tool()
    async def blender_sim_fluid_domain(
        object_name: str,
        domain_type: str = "LIQUID",
        resolution: int = 64,
        use_adaptive_domain: bool = False
    ) -> Dict[str, Any]:
        """
        设置流体域
        
        Args:
            object_name: 域对象名称（通常是包围盒）
            domain_type: 域类型 (LIQUID液体 或 GAS气体)
            resolution: 模拟分辨率
            use_adaptive_domain: 是否使用自适应域
        """
        params = FluidDomainInput(
            object_name=object_name,
            domain_type=domain_type,
            resolution=resolution,
            use_adaptive_domain=use_adaptive_domain
        )
        return await server.send_command("simulation", "fluid_domain", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_fluid_flow(
        object_name: str,
        flow_type: str = "INFLOW",
        flow_behavior: str = "GEOMETRY",
        use_initial_velocity: bool = False,
        velocity: List[float] = [0, 0, 0]
    ) -> Dict[str, Any]:
        """
        设置流体流入/流出
        
        Args:
            object_name: 流体源对象名称
            flow_type: 流类型 (INFLOW, OUTFLOW, GEOMETRY)
            flow_behavior: 流行为
            use_initial_velocity: 使用初始速度
            velocity: 速度向量 [x, y, z]
        """
        params = FluidFlowInput(
            object_name=object_name,
            flow_type=flow_type,
            flow_behavior=flow_behavior,
            use_initial_velocity=use_initial_velocity,
            velocity=velocity
        )
        return await server.send_command("simulation", "fluid_flow", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_fluid_effector(
        object_name: str,
        effector_type: str = "COLLISION"
    ) -> Dict[str, Any]:
        """
        设置流体效果器（碰撞体）
        
        Args:
            object_name: 效果器对象名称
            effector_type: 效果器类型 (COLLISION, GUIDE)
        """
        params = FluidEffectorInput(
            object_name=object_name,
            effector_type=effector_type
        )
        return await server.send_command("simulation", "fluid_effector", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_smoke_domain(
        object_name: str,
        smoke_type: str = "SMOKE",
        resolution: int = 32,
        use_high_resolution: bool = False
    ) -> Dict[str, Any]:
        """
        设置烟雾/火焰域
        
        Args:
            object_name: 域对象名称
            smoke_type: 类型 (SMOKE, FIRE, BOTH)
            resolution: 基础分辨率
            use_high_resolution: 使用高分辨率
        """
        params = SmokeDomainInput(
            object_name=object_name,
            smoke_type=smoke_type,
            resolution=resolution,
            use_high_resolution=use_high_resolution
        )
        return await server.send_command("simulation", "smoke_domain", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_smoke_flow(
        object_name: str,
        flow_type: str = "SMOKE",
        temperature: float = 1.0,
        density: float = 1.0,
        smoke_color: List[float] = [1, 1, 1]
    ) -> Dict[str, Any]:
        """
        设置烟雾/火焰发射器
        
        Args:
            object_name: 发射器对象名称
            flow_type: 流类型 (SMOKE, FIRE, BOTH)
            temperature: 温度
            density: 密度
            smoke_color: 烟雾颜色 [R, G, B]
        """
        params = SmokeFlowInput(
            object_name=object_name,
            flow_type=flow_type,
            temperature=temperature,
            density=density,
            smoke_color=smoke_color
        )
        return await server.send_command("simulation", "smoke_flow", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_ocean(
        object_name: str,
        resolution: int = 7,
        spatial_size: int = 50,
        wave_scale: float = 1.0,
        choppiness: float = 1.0,
        wind_velocity: float = 30.0,
        use_foam: bool = False
    ) -> Dict[str, Any]:
        """
        添加海洋修改器
        
        Args:
            object_name: 对象名称（通常是平面）
            resolution: 分辨率 (2^n)
            spatial_size: 空间大小
            wave_scale: 波浪缩放
            choppiness: 波涛汹涌度
            wind_velocity: 风速
            use_foam: 是否生成泡沫
        """
        params = OceanModifierInput(
            object_name=object_name,
            resolution=resolution,
            spatial_size=spatial_size,
            wave_scale=wave_scale,
            choppiness=choppiness,
            wind_velocity=wind_velocity,
            use_foam=use_foam
        )
        return await server.send_command("simulation", "ocean", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_dynamic_paint_canvas(
        object_name: str,
        surface_type: str = "PAINT",
        use_dissolve: bool = False,
        dissolve_speed: int = 80
    ) -> Dict[str, Any]:
        """
        设置动态绘制画布
        
        Args:
            object_name: 画布对象名称
            surface_type: 表面类型 (PAINT, DISPLACE, WAVE, WEIGHT)
            use_dissolve: 使用溶解效果
            dissolve_speed: 溶解速度
        """
        params = DynamicPaintCanvasInput(
            object_name=object_name,
            surface_type=surface_type,
            use_dissolve=use_dissolve,
            dissolve_speed=dissolve_speed
        )
        return await server.send_command("simulation", "dynamic_paint_canvas", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_dynamic_paint_brush(
        object_name: str,
        paint_color: List[float] = [1, 0, 0],
        paint_alpha: float = 1.0
    ) -> Dict[str, Any]:
        """
        设置动态绘制笔刷
        
        Args:
            object_name: 笔刷对象名称
            paint_color: 绘制颜色 [R, G, B]
            paint_alpha: 透明度
        """
        params = DynamicPaintBrushInput(
            object_name=object_name,
            paint_color=paint_color,
            paint_alpha=paint_alpha
        )
        return await server.send_command("simulation", "dynamic_paint_brush", params.model_dump())
    
    @mcp.tool()
    async def blender_sim_bake(
        object_name: str,
        frame_start: int = 1,
        frame_end: int = 250
    ) -> Dict[str, Any]:
        """
        烘焙模拟
        
        Args:
            object_name: 域对象名称
            frame_start: 开始帧
            frame_end: 结束帧
        """
        params = SimulationBakeInput(
            object_name=object_name,
            frame_start=frame_start,
            frame_end=frame_end
        )
        return await server.send_command("simulation", "bake", params.model_dump())
