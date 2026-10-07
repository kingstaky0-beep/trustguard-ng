import json
import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


SCAM_PATTERNS = [
    (r"\b(pay|send|transfer|deposit|fee|charge|activation)\b", 20,
     "Financial request", "The message asks the recipient to send money or pay a fee.", "high"),
    (r"\b(otp|pin|password|passcode|verification code|cvv)\b", 30,
     "Credential request", "The message appears to request sensitive authentication information.", "high"),
    (r"\b(urgent|immediately|act now|within \d+ (minutes?|hours?)|today only)\b", 15,
     "Urgency pressure", "Urgent language can be used to stop people from verifying a claim.", "medium"),
    (r"\b(congratulations|you (have )?won|winner|prize|reward|grant)\b", 15,
     "Unexpected reward", "An unexpected prize, grant, or reward is a common social-engineering lure.", "medium"),
    (r"\b(click|tap|open)\b.{0,40}\b(link|url|here)\b", 15,
     "Link pressure", "The message encourages the recipient to follow a link.", "medium"),
    (r"\b(account (will be|has been|is) (blocked|closed|suspended))\b", 15,
     "Account threat", "Threatening account closure can be used to create panic.", "medium"),
    (r"\b(bank|mtn|airtel|glo|9mobile|jamb|nyif|nyif|nysc|government)\b", 5,
     "Brand or institution claim", "The message claims an association with a recognizable institution; verify through official channels.", "low"),
]

URL_RE = re.compile(r"https?://[^\s]+", re.I)


def risk_level(score: int) -> str:
    if score <= 30:
        return "Safe"
    if score <= 60:
        return "Suspicious"
    if score <= 80:
        return "High Risk"
    return "Critical Risk"


def rule_based_analyze(text: str) -> dict[str, Any]:
    score = 0
    findings = []
    lowered = text.lower()

    for pattern, points, category, explanation, severity in SCAM_PATTERNS:
        if re.search(pattern, lowered, re.I):
            score += points
            findings.append({
                "category": category,
                "explanation": explanation,
                "severity": severity,
            })

    urls = URL_RE.findall(text)
    if urls:
        score += 10
        findings.append({
            "category": "External link",
            "explanation": "A clickable URL is present. Do not open it until the sender and domain are independently verified.",
            "severity": "medium",
        })

    if len(text) > 600:
        score += 3

    score = min(score, 100)

    if score >= 81:
        verdict = "Likely scam or dangerous social engineering"
        recommendation = "Do not send money, OTPs, PINs, passwords, or card details. Do not open suspicious links. Verify the claim through the organization's official website or phone number."
    elif score >= 61:
        verdict = "High-risk message"
        recommendation = "Pause before acting. Independently verify the sender and any financial or account claim using an official channel."
    elif score >= 31:
        verdict = "Suspicious message"
        recommendation = "Treat the message cautiously and verify the claim before clicking, paying, or sharing information."
    else:
        verdict = "No strong scam indicators detected"
        recommendation = "No strong indicators were detected, but absence of indicators does not prove a message is legitimate. Verify important requests independently."

    return {
        "risk_score": score,
        "risk_level": risk_level(score),
        "verdict": verdict,
        "findings": findings or [{
            "category": "No obvious indicators",
            "explanation": "The basic detector did not find common scam patterns.",
            "severity": "low",
        }],
        "recommendation": recommendation,
        "engine": "Rule-based",
    }


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def ai_analyze(text: str) -> dict[str, Any] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-5.5")

    instructions = """You are TrustGuard NG, an AI safety assistant focused on detecting scam and social-engineering signals in messages received by Nigerians.

Analyze the supplied message conservatively. Do not claim certainty. Look for:
- requests for money or fees
- OTP/PIN/password/card-detail requests
- urgency or threats
- fake prizes, grants, jobs, loans, investments
- impersonation of banks, telecoms, government agencies or known brands
- suspicious links
- requests to move a conversation to another channel
- unusual promises or pressure

Return ONLY valid JSON with this exact shape:
{
  "risk_score": 0,
  "risk_level": "Safe",
  "verdict": "short verdict",
  "findings": [
    {
      "category": "short category",
      "explanation": "specific explanation",
      "severity": "low"
    }
  ],
  "recommendation": "clear safety advice"
}

risk_level must be one of: Safe, Suspicious, High Risk, Critical Risk.
risk_score must be an integer from 0 to 100.
Never ask the user to provide OTPs, PINs, passwords, or other secrets.
"""

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=f"Message to analyze:\n\n{text}",
        max_output_tokens=1000,
    )

    data = _extract_json(response.output_text)

    # Basic validation and normalization before returning model output.
    score = max(0, min(100, int(data["risk_score"])))
    data["risk_score"] = score
    data["risk_level"] = risk_level(score)
    data["engine"] = "AI"
    return data


def analyze(text: str) -> dict[str, Any]:
    try:
        result = ai_analyze(text)
        if result:
            return result
    except Exception:
        # A failed model call should not make the demo unusable.
        pass

    return rule_based_analyze(text)
