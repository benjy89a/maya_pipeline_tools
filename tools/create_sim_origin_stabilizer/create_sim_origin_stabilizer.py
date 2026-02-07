"""
Module: create_sim_origin_stabilizer
Description: Simulation Origin Stabilizer Rig Generator
Date: 2026-02-07

This module provides tools to create a stabilization rig for simulation workflows.
It allows animators/FX artists to toggle between 'World Space' (original animation)
and 'Origin Space' (centered for stable simulation) using a single attribute.
"""

import logging
import maya.cmds as cmds
import maya.api.OpenMaya as om
from typing import Optional, List, Union

# 로거 설정 (Logging Setup)
# 로깅을 사용하여 디버깅 및 사용자 피드백을 체계적으로 관리합니다.
logger = logging.getLogger(__name__)
# 핸들러가 없을 경우 기본 핸들러 추가 (Maya Script Editor 출력용)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

class UndoChunk:
    """
    Context Manager for handling Maya Undo Chunks safely.
    ensures that operations can be undone in a single step,
    even if errors occur during execution.
    """
    def __init__(self, name: str = "ScriptOperation"):
        self.name = name

    def __enter__(self):
        cmds.undoInfo(openChunk=True, chunkName=self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)
        if exc_type:
            logger.error(f"Error during '{self.name}': {exc_val}")
        # 예외는 상위로 전파하여 처리하도록 함 (False 반환)
        return False

class SimStabilizer:
    """
    Class to manage the creation of the Simulation Origin Stabilizer Rig.
    
    Attributes:
        loc_name (str): The name of the reference locator/object.
        sim_target (str, optional): The object intended for simulation.
    """
    
    ATTR_NAME = "sim_space"
    ENUM_OPTS = "World:Origin:"

    def __init__(self, loc_name: str, sim_target: Optional[str] = None):
        self.loc_name = loc_name
        self.sim_target = sim_target
        self.rig_grp = None # type: Optional[str]

    def validate(self) -> bool:
        """
        Validates the input objects.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        if not cmds.objExists(self.loc_name):
            logger.error(f"Reference object not found: {self.loc_name}")
            return False
            
        if self.sim_target and not cmds.objExists(self.sim_target):
            logger.warning(f"Simulation target not found: {self.sim_target}. Continuing without target validation.")
            # Target is optional for rig creation, so we don't return False here, just warn.
        
        # Target Transform Check (Frozen Check)
        if self.sim_target and cmds.objExists(self.sim_target):
            t_val = cmds.getAttr(f"{self.sim_target}.translate")[0]
            r_val = cmds.getAttr(f"{self.sim_target}.rotate")[0]
            if any(v != 0.0 for v in t_val + r_val):
                logger.warning(
                    f"Target '{self.sim_target}' has non-zero transforms. "
                    "Ideally, simulation targets should be frozen (0,0,0) under the rig group."
                )
        
        return True

    def _get_inverse_matrix(self) -> om.MMatrix:
        """
        Calculates the inverse world matrix of the reference object.
        Using OpenMaya for precision.
        """
        sel = om.MSelectionList()
        sel.add(self.loc_name)
        dag_path = sel.getDagPath(0)
        world_mat = dag_path.inclusiveMatrix()
        return world_mat.inverse()

    def _create_rig_group(self, inv_matrix: om.MMatrix) -> str:
        """
        Creates the rig group and sets up the attributes and SDKs.
        """
        # 1. Naming: Clean and Unique
        short_name = self.loc_name.split("|")[-1].split(":")[-1]
        rig_name = f"{short_name}_stabilizer_grp"
        # cmds.createNode with name automatically handles uniqueness (e.g., rig1, rig2), 
        # but explicit uniqueName is safer for logic if needed.
        self.rig_grp = cmds.createNode("transform", name=rig_name)
        
        # 2. Store Original Matrix (Metadata)
        # 나중에 복구하거나 디버깅할 때 유용한 메타데이터
        original_mat = inv_matrix.inverse()
        cmds.addAttr(self.rig_grp, ln="originalWorldMatrix", dt="matrix")
        cmds.setAttr(f"{self.rig_grp}.originalWorldMatrix", list(original_mat), type="matrix")

        # 3. Apply Inverse Matrix (Move to Origin State)
        cmds.xform(self.rig_grp, m=list(inv_matrix), ws=True)

        # 4. Add Control Attribute
        cmds.addAttr(self.rig_grp, ln=self.ATTR_NAME, at="enum", en=self.ENUM_OPTS, k=True)
        
        # 5. Setup Set Driven Key (SDK)
        # MODE: Origin (Value=1) -> Current Position (Inverse Matrix)
        driver_plug = f"{self.rig_grp}.{self.ATTR_NAME}"
        
        # Keyframe current (Inverse) state at driver=1
        for channel in ["translate", "rotate"]:
            cmds.setDrivenKeyframe(f"{self.rig_grp}.{channel}", cd=driver_plug, dv=1)

        # MODE: World (Value=0) -> Identity Position (0,0,0)
        # Reset transform to identity
        cmds.makeIdentity(self.rig_grp, apply=False, t=1, r=1, s=0) 
        # Note: s=0 because we don't want to freeze scale by accident, though we aren't keying scale here.
        # Explicitly set to 0 just to be safe before keying
        cmds.setAttr(f"{self.rig_grp}.translate", 0, 0, 0)
        cmds.setAttr(f"{self.rig_grp}.rotate", 0, 0, 0)
        
        for channel in ["translate", "rotate"]:
            cmds.setDrivenKeyframe(f"{self.rig_grp}.{channel}", cd=driver_plug, dv=0)

        # 6. Set Default to Origin (1)
        cmds.setAttr(driver_plug, 1)
        
        return self.rig_grp

    def build(self) -> Optional[str]:
        """
        Executes the build process within an undo chunk.
        """
        if not self.validate():
            return None

        with UndoChunk(name="CreateSimStabilizer"):
            inv_m = self._get_inverse_matrix()
            rig_node = self._create_rig_group(inv_m)
            
            logger.info(f"Successfully created stabilizer rig: {rig_node}")
            
            if self.sim_target and cmds.objExists(self.sim_target):
                logger.info(f"Tip: Parent '{self.sim_target}' under '{rig_node}' to complete the setup.")

            return rig_node

def create_sim_origin_stabilizer(loc_name: str = 'locator1', sim_target: Optional[str] = None) -> Optional[str]:
    """
    Wrapper function for backward compatibility and ease of use.
    
    Args:
        loc_name (str): Name of the reference object (e.g., camera, locator).
        sim_target (str, optional): Name of the object to be stabilized.

    Returns:
        str: Name of the created rig group, or None if failed.
    """
    # 현재 선택된 객체가 있고 loc_name이 기본값이면 선택된 객체 사용
    if loc_name == 'locator1' and not cmds.objExists(loc_name):
        selection = cmds.ls(sl=True)
        if selection:
            loc_name = selection[0]
            logger.info(f"No locator specified. Using selection: {loc_name}")

    stabilizer = SimStabilizer(loc_name, sim_target)
    return stabilizer.build()

if __name__ == "__main__":
    # Test execution (Drag and drop this file to Maya script editor to test)
    # Example: Select a locator and run
    result = create_sim_origin_stabilizer()
