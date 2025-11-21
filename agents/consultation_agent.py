"""会诊协调 Agent - 负责整合多科室诊疗意见"""
from typing import Dict, List
import json
import re

from .base_agent import BaseAgent
from utils.prompt_templates import (
    CONSULTATION_COORDINATOR_TEMPLATE,
    CASE_INFO_TEMPLATE,
)


class ConsultationCoordinatorAgent(BaseAgent):
    """主持多学科会诊的 Agent"""

    def __init__(self, name: str = "会诊主持人", **kwargs):
        super().__init__(name=name, role="多学科会诊主持人", **kwargs)

    def run_consultation(
        self,
        patient_agent,
        department_sessions: List[Dict],
    ) -> Dict:
        """发起多科室会诊并返回结构化结果"""
        case_info = self._build_case_info(patient_agent)
        examination_summary = self._summarize_examinations(patient_agent)
        department_findings = self._summarize_department_findings(department_sessions)

        prompt = CONSULTATION_COORDINATOR_TEMPLATE.format(
            case_info=case_info,
            examination_summary=examination_summary,
            department_findings=department_findings,
        )

        response = self.generate_response(
            prompt,
            system_message="你是一位负责多学科会诊的专家，需要整合各专科意见给出最终方案。",
        )

        return self._parse_response(response)

    def _build_case_info(self, patient_agent) -> str:
        medical_history = ", ".join(patient_agent.medical_history) if patient_agent.medical_history else "无"
        symptoms = ", ".join(patient_agent.symptoms[:8])
        return CASE_INFO_TEMPLATE.format(
            age=patient_agent.age,
            gender=patient_agent.gender,
            chief_complaint=symptoms or "不适",
            symptoms=symptoms or "未提供",
            medical_history=medical_history,
            vital_signs="暂无",
            additional_info=""
        )

    def _summarize_examinations(self, patient_agent) -> str:
        if not patient_agent.examination_reports:
            return "暂无检查"

        lines = []
        for exam, report in patient_agent.examination_reports.items():
            conclusion = ""
            if isinstance(report, dict):
                conclusion = report.get("conclusion") or report.get("findings", "")
            lines.append(f"- {exam}: {conclusion[:80]}")
        return "\n".join(lines)

    def _summarize_department_findings(self, sessions: List[Dict]) -> str:
        if not sessions:
            return "尚未有科室诊断"

        summaries = []
        for session in sessions:
            diagnosis = session.get("diagnosis", {})
            disease = diagnosis.get("disease", "待定")
            confidence = diagnosis.get("confidence", "unknown")
            rationale = diagnosis.get("diagnosis_reasoning", "无详细说明")
            summaries.append(
                f"【{session.get('department')}】医生: {session.get('doctor')}\n"
                f"- 诊断: {disease} (置信度: {confidence})\n"
                f"- 依据: {rationale[:120]}\n"
            )
        return "\n".join(summaries)

    def _parse_response(self, response: str) -> Dict:
        try:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as exc:
            print(f"解析会诊响应失败: {exc}")

        return {
            "final_diagnosis": None,
            "rationale": response,
            "treatment_plan": {},
            "follow_up": {},
        }
