from flask import Flask, jsonify, request
from flask_cors import CORS
import re

PORT = 8000
app = Flask(__name__)
CORS(app)

# Suspicious/uncommon domains often used in phishing
SUSPICIOUS_DOMAINS_ENDINGS = {
    '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.buzz', 
    '.club', '.work', '.click', '.link', '.info', '.ru', '.cn',
    '.bit.ly', '.tinyurl', '.t.co', '.goo.gl'
}

# URL prefixes
URL_PREFIXES = {
    'http://', 'https://', 'www.'
}

# Well-known legitimate domains
LEGITIMATE_DOMAINS = {
    'paypal.com', 'google.com', 'gmail.com', 'googlemail.com',
    'amazon.com', 'microsoft.com', 'apple.com', 'outlook.com',
    'yahoo.com', 'hotmail.com', 'live.com', 'icloud.com',
    'facebook.com', 'netflix.com', 'linkedin.com', 'twitter.com',
    'instagram.com', 'ebay.com', 'dropbox.com', 'adobe.com',
    'chase.com', 'bankofamerica.com', 'wellsfargo.com', 'citibank.com',
}

# Common substitutions often used in typosquatting (spoofed addresses)
COMMON_SUBSTITUTIONS = {
    '0': 'o',
    '1': 'l',
    '|': 'l',
    '5': 's',
}

"""
Check if the domain is suspicious
@param domain: domain to check
@return: True if the domain is suspicious, False otherwise
"""
def is_suspicious_domain(domain):
    # Spoofed uppercase lookalike (e.g. PaypAL.com, Google.com) -> suspicious
    lowered_domain = domain.lower()
    if lowered_domain in LEGITIMATE_DOMAINS and lowered_domain != domain:
        return True

    # Suspicious domain endings check
    for ending in SUSPICIOUS_DOMAINS_ENDINGS:
        if domain.endswith(ending):
            return True

    # Common substitutions check
    subsitute_domain = ''
    for letter in lowered_domain:
        if letter in COMMON_SUBSTITUTIONS:
            subsitute_domain += COMMON_SUBSTITUTIONS[letter]
        else:
            subsitute_domain += letter

    # Spoofed lookalike check
    if subsitute_domain in LEGITIMATE_DOMAINS and subsitute_domain != domain:
        return True
    return False

"""
Check if the word is a suspicious link
@param word: word to check
@return: True if the word is a suspicious link, False otherwise
"""
def is_suspicious_link(word):
    # URL prefix check
    is_url = False
    for url in URL_PREFIXES:
        if word.lower().startswith(url):
            is_url = True
            break
    if not is_url:
        return False
    
    # Split word into url and domain
    splitted_word = word.split('//', 1)
    if len(splitted_word) == 1:
        splitted_word = word.split('.', 1)

    domain = splitted_word[1]
    hostname = domain.split('/')[0].split('?')[0]  # strip path/query

    # IP address check - flag IP-based URLs as suspicious (before domain format check)
    parts = hostname.split('.')
    if len(parts) == 4:
        try:
            if all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                return True
        except (ValueError, IndexError):
            pass

    # Domain format check
    if '.' not in hostname or hostname.count('.') != 1:
        return False

    # Check for suspicious domains
    if is_suspicious_domain(hostname):
        return True

    return False

"""
Check if the word is a suspicious email
@param word: word to check
@return: True if the word is a suspicious email, False otherwise
"""
def is_suspicious_email(word):
    # '@' symbol check
    if '@' not in word or word.count('@') != 1:
        return False
    
    # Split email into username and domain
    split_email = word.split('@')
    if len(split_email) != 2 or not split_email[0] or not split_email[1]:
        return False

    # Domain format check
    domain = split_email[1]
    if '.' not in domain or domain.count('.') != 1:
        return False

    # Check for suspicious domains
    if is_suspicious_domain(domain):
        return True

    return False

"""
Check if the word is using suspicious words
@param word: word to check
@return: True if the word is using suspicious words, False otherwise
"""
def is_suspicious_word(word):
    suspicious_words_single = {
        'urgent', 'immediately', 'asap', 'suspended', 'expired', 'verify',
        'confirm', 'click', 'update', 'limited', 'required', 'must',
        'now', 
    }

    if word.lower() in suspicious_words_single:
        return True
    return False

"""
Calculate the suspicious percentage of the word
@param word: word to calculate the suspicious percentage
@return: suspicious percentage of the word
"""
def suspicious_percentage(word):
    if is_suspicious_link(word) or is_suspicious_email(word):
        # Return 100% if the word is a suspicious link or email
        return 100
    elif is_suspicious_word(word):
        # Return 10% if the word is using suspicious words
        return 10
    else:
        return 0


"""
Detect if the text file is a phishing email
@param textFile: text file to check
@return: jsonify object with the response, suspicious words, and suspicious percentage
"""
@app.route("/checkMailPhishing", methods=["POST"])
def checkMailPhishing():
    # Variables
    suspicious_words = []        # Suspicious words list
    sus_percentage = 0           # Suspicious percentage
    
    # Get the text file from the request
    textFile = request.json.get("textFile")
    if not textFile:
        return jsonify(error="No text file inserted", status=400)

    try:
        print("Text file received with length: " + str(len(textFile)))

        # Split text into words and check each if is suspicious
        text_splitted = textFile.split()
        new_words = []

        for word in text_splitted:
            # Remove common punctuation for matching
            word_clean = word.strip('.,!?:;()[] \n\t')

            # Get the suspicious percentage of the word
            percentage = suspicious_percentage(word_clean) if word_clean else 0

            # If the word is suspicious, add it to the new words list and update the suspicious words list and percentage
            if percentage > 0:
                new_words.append(f"<b style='color: red;'>{word}</b>")
                suspicious_words.append(word)
                sus_percentage += percentage
            else:
                new_words.append(word)
        
        new_text_file = ' '.join(new_words)
        return jsonify(response=new_text_file, status=200, suspiciousWords=suspicious_words, susPercentage=min(100, sus_percentage))
    except Exception as e:
        print("Error checking mail phishing: " + str(e))
        return jsonify(response="Error checking mail phishing", status=500)

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
