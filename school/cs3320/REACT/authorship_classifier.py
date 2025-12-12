import re
import sys
import json
from collections import Counter


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def strip_tags(html):
    # remove script/style blocks first
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    # remove comments
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    # remove tags
    text = re.sub(r"<[^>]+>", " ", html)
    # collapse whitespace
    return re.sub(r"\s+", " ", text).strip()


def extract_scripts(html):
    # return list of script contents
    return re.findall(r"(?is)<script[^>]*>(.*?)</script>", html)


def word_stats(text):
    words = re.findall(r"\b[\w']+\b", text)
    words_lc = [w.lower() for w in words]
    total = len(words_lc)
    unique = len(set(words_lc))
    ttr = unique / total if total else 0
    avg_word_len = sum(len(w) for w in words_lc) / total if total else 0
    return {
        'total_words': total,
        'unique_words': unique,
        'type_token_ratio': round(ttr, 4),
        'avg_word_len': round(avg_word_len, 2)
    }


def sentence_stats(text):
    sents = re.split(r'[.!?]+\s+', text)
    sents = [s for s in sents if s.strip()]
    total_sents = len(sents)
    words = sum(len(re.findall(r"\b[\w']+\b", s)) for s in sents)
    avg_sent_len = words / total_sents if total_sents else 0
    return {'total_sentences': total_sents, 'avg_sentence_len': round(avg_sent_len, 2)}


def punctuation_stats(text):
    counts = Counter(ch for ch in text if not ch.isalnum() and not ch.isspace())
    total_chars = len(text)
    return {'punctuation_counts': dict(counts), 'punctuation_density': round(sum(counts.values())/total_chars if total_chars else 0, 4)}


def detect_nested_ul_bug(html):
    # crude detection: <ul> directly followed by <ul> without an intervening </li>
    return bool(re.search(r"<ul[^>]*>\s*<ul[^>]*>", html, flags=re.I))


def detect_assignment_text(text):
    patterns = [r"project requirements", r"at least 4 components", r"stateful component", r"show current time"]
    for p in patterns:
        if re.search(p, text, flags=re.I):
            return True
    return False


def analyze_code_features(scripts):
    joined = '\n'.join(scripts)
    features = {}
    features['num_scripts'] = len(scripts)
    features['has_react_createRoot'] = bool(re.search(r"createRoot\(", joined))
    features['num_class_components'] = len(re.findall(r"class\s+[A-Z][A-Za-z0-9_]*\s+extends\s+React\.Component", joined))
    features['num_function_components'] = len(re.findall(r"function\s+[A-Z][A-Za-z0-9_]*\s*\(|const\s+[A-Z][A-Za-z0-9_]*\s*=\s*\(|let\s+[A-Z][A-Za-z0-9_]*\s*=\s*\(", joined))
    features['uses_inline_styles'] = bool(re.search(r"style=\{", joined))
    features['has_aria_live'] = bool(re.search(r"aria-live=\"", joined))
    features['mentions_this'] = bool(re.search(r"this\.state|this\.props", joined))
    features['uses_babel_script_type'] = bool(re.search(r"type=\"text/babel\"", joined))
    features['contains_assignment_strings'] = detect_assignment_text(joined)
    return features


def score_heuristic(html, text, scripts):
    score = 50.0  # start at neutral 50
    reasons = []

    # assignment text -> strong human signal
    if detect_assignment_text(text):
        score += 30
        reasons.append((+30, 'Contains explicit assignment instructions / "Project Requirements"'))

    # nested UL bug -> human
    if detect_nested_ul_bug(html):
        score += 15
        reasons.append((+15, 'Detected nested <ul> without <li> (likely human oversight)'))

    # external odd image url
    if re.search(r"encrypted-tbn0\.gstatic\.com|googleusercontent", html):
        score += 5
        reasons.append((+5, 'Uses specific Google thumbnail image URL (typical of manual copy-paste)'))

    # presence of aria roles, small semantics -> human
    if re.search(r"role=\"(banner|application|main|contentinfo)\"", html):
        score += 6
        reasons.append((+6, 'Contains explicit ARIA roles (human or careful author)'))

    # lots of modern API tokens (neutral)
    code_features = analyze_code_features(scripts)
    if code_features['has_react_createRoot']:
        score += 2
    if code_features['num_class_components'] >= 1 and code_features['num_function_components'] >= 2:
        score += 3

    # very short avg sentence length + low TTR -> AI-like
    ws = word_stats(text)
    ss = sentence_stats(text)
    if ss['avg_sentence_len'] < 6 and ws['type_token_ratio'] < 0.4:
        score -= 20
        reasons.append((-20, 'Short sentences and low lexical variety (can be AI-like)'))

    # very high lexical variety -> human
    if ws['type_token_ratio'] > 0.6:
        score += 6
        reasons.append((+6, 'High type-token ratio (rich vocabulary)'))

    # punctuation density heuristics
    ps = punctuation_stats(text)
    if ps['punctuation_density'] > 0.15:
        score -= 4
        reasons.append((-4, 'High punctuation density (could be templated/AI)'))

    # clamp
    score = max(0.0, min(100.0, score))
    return round(score, 1), reasons, {'word_stats': ws, 'sentence_stats': ss, 'punctuation_stats': ps, 'code_features': code_features}


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    try:
        html = read_file(path)
    except Exception as e:
        print(json.dumps({'error': f'Failed to read {path}: {e}'}))
        return

    text = strip_tags(html)
    scripts = extract_scripts(html)

    score, reasons, diagnostics = score_heuristic(html, text, scripts)

    out = {
        'path': path,
        'score_human_likelihood_percent': score,
        'verdict': 'likely-human' if score >= 60 else ('likely-ai' if score <= 40 else 'uncertain'),
        'reasons': [{'delta': d, 'explanation': e} for d, e in reasons],
        'diagnostics': diagnostics,
    }

    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
