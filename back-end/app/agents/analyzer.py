# app/agents/analyzer.py
from app.schemas import AnalysisResult
from app.utils.llm import call_llm
import json
import re

SYSTEM = """You are a support ticket analyzer.
Return only valid JSON with fields: summary, keywords.
"""
def call_llm(system: str, prompt: str, temperature: float = 0):
  # Minimal analyzer: disable external LLM and force local fallback
  return None
def _fallback_analysis(text: str) -> AnalysisResult:
  clean = re.sub(r"\s+", " ", text).strip()
  summary = clean[:200] if clean else ""
  tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", clean.lower())
  stop = {"the","a","an","and","or","for","to","of","in","on","with","without","my","your","i","you","he","she","we","they","is","are","be","been","le","la","les","un","une","des","de","du","dans","et","ou","pour","sur","avec","sans","mon","ma","mes","votre","vos","je","tu","il","elle","nous","vous","ils","elles","ne","pas","au","aux","ce","cet","cette","ces","est","été","être"}
  keywords = []
  seen = set()
  for t in tokens:
    if t in stop or len(t) < 3:
      continue
    if t not in seen:
      seen.add(t)
      keywords.append(t)
    if len(keywords) >= 8:
      break
  if not keywords and clean:
    keywords = [clean.split()[0]]
  return AnalysisResult(summary=summary, keywords=keywords)

JSON_SCHEMA_EXAMPLE = (
  '{\n'
  '  "summary": "...",\n'
  '  "keywords": ["..."]\n'
  '}'
)

def analyze_ticket(text: str) -> AnalysisResult:
  """
  Analyze a support ticket to extract a summary and keywords.
  Parameters:
  - text: the content of the support ticket
  Returns:
  - AnalysisResult containing the summary and keywords
  """
  prompt = (
    "Summarize the ticket in less than a hundred words and extract 5 to 10 keywords.\n"
    "Ticket:\n"
    + (text or "") + "\n\n"
    "JSON format:\n"
    + JSON_SCHEMA_EXAMPLE + "\n"
  )
  output = None
  try:
    output = call_llm(SYSTEM, prompt, temperature=0)
    if not output or not isinstance(output, str):
      return _fallback_analysis(text)
    return AnalysisResult(**json.loads(output))
  except Exception:
    try:
      if output:
        m = re.search(r"\{.*\}", output, re.DOTALL)
        if m:
          return AnalysisResult(**json.loads(m.group()))
    except Exception:
      pass
    return _fallback_analysis(text)
