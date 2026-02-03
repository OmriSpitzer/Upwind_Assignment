from flask import Flask, jsonify, request
from flask_cors import CORS
import re

PORT = 8000
app = Flask(__name__)
CORS(app)

# Suspicious/uncommon domains often used in phishing
SUSPICIOUS_DOMAINS = [
    '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.buzz', 
    '.club', '.work', '.click', '.link', '.info', '.ru', '.cn',
    '.bit.ly', '.tinyurl', '.t.co', '.goo.gl'
]
URL_PREFIXES = ['http://', 'https://', 'www.']

# Well-known legitimate domains (used to detect spoofed lookalikes)
LEGITIMATE_DOMAINS = {
    'paypal.com', 'google.com', 'gmail.com', 'googlemail.com',
    'amazon.com', 'microsoft.com', 'apple.com', 'outlook.com',
    'yahoo.com', 'hotmail.com', 'live.com', 'icloud.com',
    'facebook.com', 'netflix.com', 'linkedin.com', 'twitter.com',
    'instagram.com', 'ebay.com', 'dropbox.com', 'adobe.com',
    'chase.com', 'bankofamerica.com', 'wellsfargo.com', 'citibank.com',
}

# Urgent/suspicious language often used in phishing to pressure the reader
SUSPICIOUS_WORDS = {
    'urgent', 'immediately', 'asap', 'action required', 'verify now',
    'confirm now', 'suspended', 'expired', 'limited time', 'act now',
    'click here', 'verify your account', 'update your account',
    'confirm your identity', 'urgent action', 'immediate action',
    'your account', 'verify', 'confirm', 'suspicious activity',
}
# Single-word variants for token-level check (multi-word handled in text)
SUSPICIOUS_WORDS_SINGLE = {
    'urgent', 'immediately', 'asap', 'suspended', 'expired', 'verify',
    'confirm', 'click', 'update', 'limited', 'action', 'required',
}

# Character substitutions often used in typosquatting (spoofed addresses)
# Maps spoof chars to canonical: 0->o, 1->l, |->l, 5->s so paypa1->paypal, g00gle->google
SPOOF_SUBSTITUTIONS = str.maketrans('01|5', 'olls')

def isSuspiciousLink(word):
    if not any(prefix in word.lower() for prefix in URL_PREFIXES):
        return False
    
    # Check for IP address in URL (e.g., http://192.168.1.1/path)
    ip_pattern = r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    if re.search(ip_pattern, word):
        return True
    
    # Check for suspicious domains
    word_lower = word.lower()
    for domain in SUSPICIOUS_DOMAINS:
        if domain in word_lower:
            return True
    
    return False

def _normalize_for_spoof_check(domain):
    """Normalize domain for typosquatting check (e.g. paypa1 -> paypal)."""
    d = domain.lower().strip()
    return d.translate(SPOOF_SUBSTITUTIONS)

def _domain_looks_like_legitimate(domain):
    """True only if domain is an exact match to a known legitimate domain (not normalized)."""
    if not domain:
        return False
    return domain.lower() in LEGITIMATE_DOMAINS

def _domain_is_spoofed_lookalike(domain):
    """True if domain looks like a legitimate one but has minor differences (spoofed)."""
    if not domain or '@' in domain:
        return False
    domain = domain.lower()
    norm = _normalize_for_spoof_check(domain)
    # Exact match -> legitimate
    if domain in LEGITIMATE_DOMAINS:
        return False
    # Typosquatting: e.g. paypa1.com, g00gle.com — normalizes to same as a legit domain but differs
    for legit in LEGITIMATE_DOMAINS:
        if _normalize_for_spoof_check(legit) == norm and domain != legit:
            return True
    # Brand + suffix: e.g. paypal-security.com, google-verify.com (not the real domain)
    for legit in LEGITIMATE_DOMAINS:
        base = legit.split('.')[0]
        if (domain.startswith(base + '-') or domain.startswith(base + '.')) and domain != legit:
            return True
    return False

def isSuspiciousEmail(word):
    """Check for spoofed sender addresses (look similar to legitimate but have minor differences)."""
    if not word or '@' not in word:
        return False
    # Basic email shape
    parts = word.split('@')
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False

    domain = parts[1].strip().lower()
    if not domain or '.' not in domain:
        return False

    # Legitimate sender: domain is exactly known -> not suspicious
    if _domain_looks_like_legitimate(domain):
        return False
    # Spoofed lookalike (e.g. paypa1.com, g00gle.com) -> suspicious
    if _domain_is_spoofed_lookalike(domain):
        return True
    return False

def isUsingSuspiciousWords(word):
    """Check for urgent/suspicious language (e.g. urgent, immediately, action required)."""
    if not word or not isinstance(word, str):
        return False
    w = word.lower().strip()
    # Remove common punctuation for matching
    w_clean = re.sub(r'[^\w\s]', '', w)
    if w_clean in SUSPICIOUS_WORDS_SINGLE:
        return True
    # Check against full set (handles "action required" etc. when passed as phrase)
    if w in SUSPICIOUS_WORDS or w_clean in SUSPICIOUS_WORDS:
        return True
    return False

@app.route("/checkMailPhishing", methods=["POST"])
def checkMailPhishing():
    suspiciousWords = []
    susPercentage = 0
    
    try:
        textFile = request.json.get("textFile")
        if not textFile:
            return jsonify(response="No text file inserted", status=400)
        print("Text file received with length: " + str(len(textFile)))

        # Split text into words and check each for suspicious links
        words = textFile.split()
        newWords = []
        for word in words:
            if isSuspiciousLink(word) or isSuspiciousEmail(word):
                newWords.append(f"<b style='color: red;'>{word}</b>")
                suspiciousWords.append(word)
                susPercentage = 100
            elif isUsingSuspiciousWords(word):
                newWords.append(f"<b style='color: red;'>{word}</b>")
                suspiciousWords.append(word)
                susPercentage = min(100, susPercentage + 10)
            else:
                newWords.append(word)
        
        newTextFile = ' '.join(newWords)
        return jsonify(response=newTextFile, status=200, suspiciousWords=suspiciousWords, susPercentage=susPercentage)
    except Exception as e:
        print("Error checking mail phishing: " + str(e))
        return jsonify(response="Error checking mail phishing", status=500)

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
