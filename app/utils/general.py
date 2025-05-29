from urllib.parse import urlparse
from difflib import SequenceMatcher

def is_valid_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False

def similarity_score(s1: str, s2: str) -> float:
  if not s1 or not s2:
      return 0
  return SequenceMatcher(None, s1.lower(), s2.lower()).ratio()