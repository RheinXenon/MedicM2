"""
示例病例 - 用于测试系统
"""

# 示例病例1：疑似急性冠脉综合征
CASE_ACS = {
    "patient_info": {
        "age": 55,
        "gender": "男",
        "chief_complaint": "持续胸痛3天，伴有呼吸困难"
    },
    "symptoms": [
        "胸部中央压榨性疼痛",
        "疼痛放射到左臂和下颌",
        "呼吸急促",
        "大汗淋漓",
        "恶心",
        "濒死感"
    ],
    "medical_history": [
        "高血压10年",
        "糖尿病5年",
        "吸烟史30年",
        "高脂血症"
    ],
    "vital_signs": {
        "血压": "160/95 mmHg",
        "心率": "102次/分",
        "体温": "37.2°C",
        "血氧饱和度": "94%",
        "呼吸频率": "22次/分"
    }
}

# 示例病例2：疑似脑卒中
CASE_STROKE = {
    "patient_info": {
        "age": 68,
        "gender": "女",
        "chief_complaint": "突发左侧肢体无力2小时"
    },
    "symptoms": [
        "左侧肢体无力",
        "左侧面部麻木",
        "言语不清",
        "头晕",
        "视物模糊"
    ],
    "medical_history": [
        "高血压15年",
        "房颤5年",
        "未规律服用抗凝药"
    ],
    "vital_signs": {
        "血压": "180/100 mmHg",
        "心率": "不规则，约90次/分",
        "体温": "36.8°C",
        "血氧饱和度": "97%"
    }
}

# 示例病例3：疑似肺癌
CASE_LUNG_CANCER = {
    "patient_info": {
        "age": 62,
        "gender": "男",
        "chief_complaint": "咳嗽、痰中带血1个月，进行性消瘦"
    },
    "symptoms": [
        "持续咳嗽",
        "痰中带血",
        "体重下降10kg/2月",
        "胸痛",
        "声音嘶哑",
        "乏力"
    ],
    "medical_history": [
        "吸烟史40年，每天2包",
        "慢性阻塞性肺病",
        "否认肺结核史"
    ],
    "vital_signs": {
        "血压": "130/80 mmHg",
        "心率": "88次/分",
        "体温": "37.5°C",
        "血氧饱和度": "92%",
        "呼吸频率": "20次/分"
    }
}

# 示例病例4：疑似急性胰腺炎
CASE_PANCREATITIS = {
    "patient_info": {
        "age": 45,
        "gender": "男",
        "chief_complaint": "剧烈上腹痛6小时，向腰背部放射"
    },
    "symptoms": [
        "持续性剧烈上腹痛",
        "疼痛向腰背部放射",
        "恶心、呕吐",
        "腹胀",
        "发热"
    ],
    "medical_history": [
        "长期大量饮酒",
        "高脂血症",
        "2年前胆囊结石"
    ],
    "vital_signs": {
        "血压": "110/70 mmHg",
        "心率": "115次/分",
        "体温": "38.5°C",
        "血氧饱和度": "96%"
    }
}

# 示例病例5：复杂病例 - 多系统受累
CASE_COMPLEX = {
    "patient_info": {
        "age": 72,
        "gender": "女",
        "chief_complaint": "胸闷、气短加重1周，伴双下肢水肿"
    },
    "symptoms": [
        "劳力性呼吸困难",
        "夜间阵发性呼吸困难",
        "双下肢水肿",
        "尿量减少",
        "食欲不振",
        "腹胀",
        "乏力"
    ],
    "medical_history": [
        "冠心病10年，曾行支架植入术",
        "高血压20年",
        "糖尿病15年",
        "慢性肾功能不全3年",
        "房颤"
    ],
    "vital_signs": {
        "血压": "150/90 mmHg",
        "心率": "不规则，约110次/分",
        "体温": "36.5°C",
        "血氧饱和度": "90%",
        "呼吸频率": "26次/分"
    }
}


# 所有示例病例
ALL_CASES = {
    "急性冠脉综合征": CASE_ACS,
    "脑卒中": CASE_STROKE,
    "肺癌": CASE_LUNG_CANCER,
    "急性胰腺炎": CASE_PANCREATITIS,
    "复杂病例": CASE_COMPLEX
}


def get_case(case_name: str):
    """
    获取指定名称的示例病例
    
    Args:
        case_name: 病例名称
        
    Returns:
        病例数据字典
    """
    return ALL_CASES.get(case_name)


def list_cases():
    """列出所有可用的示例病例"""
    print("可用的示例病例：")
    for i, name in enumerate(ALL_CASES.keys(), 1):
        print(f"{i}. {name}")


if __name__ == "__main__":
    list_cases()
