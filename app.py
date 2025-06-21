from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import time
import os
from datetime import datetime
import sqlite3
import json
import requests
import re

app = Flask(__name__)
CORS(app)

print("Starting MINIMAL DEBUG VERSION - Author Detection Only...")

def init_db():
    conn = sqlite3.connect('analyses.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash TEXT UNIQUE,
            content_type TEXT,
            confidence_score REAL,
            verdict TEXT,
            analysis_details TEXT,
            file_metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

def debug_show_all_lines(content):
    """
    Show EVERY line with detailed debugging
    """
    print("\n" + "="*80)
    print("🔍 COMPLETE LINE-BY-LINE ANALYSIS")
    print("="*80)
    
    lines = content.strip().split('\n')
    
    print(f"📊 TOTAL LINES: {len(lines)}")
    print(f"📄 CONTENT LENGTH: {len(content)} characters")
    print("\n" + "-"*80)
    
    for i, line in enumerate(lines):
        line = line.strip()
        print(f"LINE {i+1:2d}: '{line}'")
        print(f"       Length: {len(line)} chars")
        
        if not line:
            print("       STATUS: ❌ EMPTY - SKIP")
        elif any(word in line.lower() for word in ['ago', 'hours', 'minutes']):
            print("       STATUS: ⏰ TIMESTAMP - SKIP")
        elif len(line) > 50:
            print("       STATUS: 📰 TOO LONG (HEADLINE) - SKIP")
        elif any(word in line.lower() for word in ['fired', 'reports', 'says', 'announces']):
            print("       STATUS: 📢 HEADLINE WORDS - SKIP")
        elif re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)$', line):
            print(f"       STATUS: ✅ POTENTIAL AUTHOR PATTERN MATCH!")
            print(f"       CANDIDATE: '{line}'")
            
            # Check exclusions
            exclusions = ['Donald Trump', 'Joe Biden', 'Barack Obama']
            if line in exclusions:
                print(f"       FINAL: ❌ EXCLUDED (political figure)")
            else:
                print(f"       FINAL: ✅ VALID AUTHOR: '{line}'")
        else:
            print("       STATUS: ❓ OTHER PATTERN")
        
        print()
    
    print("="*80)

def extract_author_simple(content):
    """
    ULTRA SIMPLE author extraction with maximum debugging
    """
    print("\n🚀 STARTING ULTRA SIMPLE AUTHOR EXTRACTION")
    
    debug_show_all_lines(content)
    
    lines = content.strip().split('\n')
    
    print("\n🔍 NOW SEARCHING FOR AUTHOR...")
    
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        
        print(f"\n🔎 CHECKING LINE {i+1}: '{line}'")
        
        # Skip empty
        if not line:
            print("   ⏭️ Skip: empty")
            continue
            
        # Skip timestamps
        if any(word in line.lower() for word in ['ago', 'hours', 'minutes']):
            print("   ⏭️ Skip: timestamp")
            continue
            
        # Skip long lines (headlines)
        if len(line) > 50:
            print("   ⏭️ Skip: too long")
            continue
            
        # Skip headline words
        if any(word in line.lower() for word in ['fired', 'reports', 'says', 'announces', 'hundreds']):
            print("   ⏭️ Skip: headline words")
            continue
        
        # Check for two-word name pattern
        pattern_match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)$', line)
        
        if pattern_match:
            candidate = pattern_match.group(1)
            print(f"   ✅ PATTERN MATCH: '{candidate}'")
            
            # Explicit exclusions
            exclusions = [
                'Donald Trump', 'Joe Biden', 'Barack Obama', 'Kamala Harris',
                'New York', 'Los Angeles', 'BBC News', 'Getty Images'
            ]
            
            print(f"   🔍 Checking against exclusions: {exclusions}")
            
            if candidate in exclusions:
                print(f"   ❌ EXCLUDED: '{candidate}' is in exclusion list")
                continue
            else:
                print(f"   ✅ FOUND VALID AUTHOR: '{candidate}'")
                print(f"   🎉 RETURNING: '{candidate}'")
                return candidate
        else:
            print("   ❓ No pattern match")
    
    print("\n❌ NO AUTHOR FOUND")
    return None

def minimal_analysis(content):
    """
    MINIMAL analysis focusing only on author detection
    """
    print("\n" + "🚀" * 20)
    print("STARTING MINIMAL ANALYSIS")
    print("🚀" * 20)
    
    # Extract author with maximum debugging
    detected_author = extract_author_simple(content)
    
    print(f"\n🏆 FINAL DETECTED AUTHOR: '{detected_author}'")
    
    # Minimal source detection
    if 'bbc news' in content.lower():
        source = 'BBC News'
        score = 82
    else:
        source = 'Unknown'
        score = 50
    
    result = {
        "success": True,
        "detected_author": detected_author,
        "source": source,
        "credibility_score": score,
        "method": "Minimal Debug Analysis",
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\n🎯 RETURNING RESULT:")
    print(f"   Author: '{result['detected_author']}'")
    print(f"   Source: {result['source']}")
    print(f"   Score: {result['credibility_score']}")
    
    return result

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': 'MINIMAL DEBUG v1.0 - Author Detection Only',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/analyze/news-misinformation', methods=['POST'])
def analyze_news_misinformation():
    """
    MINIMAL debug endpoint - focuses only on author detection
    """
    try:
        print("\n" + "🔥" * 50)
        print("NEW REQUEST RECEIVED")
        print("🔥" * 50)
        
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            }), 400
        
        print(f"\n📥 RECEIVED CONTENT ({len(content)} chars)")
        print(f"📄 Content preview: {content[:100]}...")
        
        # Run minimal analysis
        analysis_result = minimal_analysis(content)
        
        # Store in database
        content_hash = get_content_hash(content)
        
        try:
            conn = sqlite3.connect('analyses.db')
            conn.execute('''
                INSERT OR REPLACE INTO analyses
                (content_hash, content_type, confidence_score, verdict, analysis_details, file_metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, 'minimal_debug', analysis_result['credibility_score'], 'debug',
                  json.dumps(analysis_result), json.dumps({'type': 'minimal_debug'})))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
        
        # Format minimal response
        response = {
            'success': True,
            'analysis_id': f'DEBUG-{content_hash[:8]}',
            'detected_author': analysis_result['detected_author'],
            'source': analysis_result['source'],
            'credibility_score': analysis_result['credibility_score'],
            'method': analysis_result['method'],
            'timestamp': analysis_result['timestamp']
        }
        
        print(f"\n📤 SENDING RESPONSE:")
        print(f"   detected_author: '{response['detected_author']}'")
        print(f"   source: {response['source']}")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
