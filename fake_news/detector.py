"""
Enhanced Smart Fake News Detector v2.0
--------------------------------------
Improvements:
1. Better entity extraction with multi-word support
2. Structured fact verification
3. Multi-factor confidence scoring
4. Improved negation detection
5. Source credibility ranking
6. Temporal context analysis
7. Claim type classification
8. Uncertainty handling
"""

import os
import re
import requests
from datetime import datetime, timedelta
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import nltk

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass


class EnhancedFakeNewsDetector:
    """
    Production-ready fake news detector with advanced NLP and fact verification
    """
    
    def __init__(self, news_api_key):
        self.news_api_key = news_api_key
        self.news_base_url = "https://newsapi.org/v2"
        
        # Enhanced configuration
        self.MIN_SIMILARITY = 0.50  # Raised from 0.2
        self.HIGH_CONFIDENCE_SIMILARITY = 0.75
        self.MIN_SOURCES_FOR_VERIFICATION = 2
        
        # Credible news sources (ranked by reliability)
        self.credible_sources = {
            'tier1': ['Reuters', 'Associated Press', 'BBC News', 'The Guardian', 'NPR'],
            'tier2': ['CNN', 'The New York Times', 'The Washington Post', 'Bloomberg', 'Financial Times'],
            'tier3': ['USA Today', 'NBC News', 'ABC News', 'CBS News', 'The Wall Street Journal']
        }
        
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but'])
    
    # ========================================
    # ENHANCED CLAIM ANALYSIS
    # ========================================
    
    def identify_claim_type(self, text):
        """
        Classify the type of claim:
        - factual: Verifiable facts (who, what, when, where)
        - opinion: Subjective statements
        - prediction: Future events
        - ambiguous: Unclear or mixed
        """
        text_lower = text.lower()
        
        # Opinion indicators
        opinion_words = ['should', 'believe', 'think', 'feel', 'opinion', 'best', 'worst', 
                        'probably', 'likely', 'might', 'could', 'seems', 'appears']
        
        # Prediction indicators
        prediction_words = ['will', 'going to', 'predict', 'forecast', 'expect', 
                          'next year', 'future', 'upcoming', 'soon']
        
        # Factual indicators (verbs of being/action)
        factual_verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 
                        'won', 'lost', 'became', 'appointed', 'elected', 'died']
        
        opinion_count = sum(1 for word in opinion_words if word in text_lower)
        prediction_count = sum(1 for word in prediction_words if word in text_lower)
        factual_count = sum(1 for word in factual_verbs if word in text_lower)
        
        if prediction_count >= 2:
            return 'prediction'
        elif opinion_count >= 2:
            return 'opinion'
        elif factual_count >= 1:
            return 'factual'
        else:
            return 'ambiguous'
    
    def extract_named_entities(self, text):
        """
        Extract named entities with better multi-word support
        """
        entities = []
        
        # Method 1: Capitalized sequences (multi-word)
        # "Narendra Modi" = one entity, not two
        words = text.split()
        current_entity = []
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if clean_word and len(clean_word) > 1:
                # Check if capitalized and not at sentence start
                if clean_word[0].isupper() and (i == 0 or not words[i-1].endswith('.')):
                    current_entity.append(clean_word)
                else:
                    # End of entity sequence
                    if current_entity:
                        entity = ' '.join(current_entity)
                        if entity.lower() not in self.stop_words:
                            entities.append(entity)
                        current_entity = []
        
        # Don't forget last entity
        if current_entity:
            entity = ' '.join(current_entity)
            if entity.lower() not in self.stop_words:
                entities.append(entity)
        
        # Method 2: Use POS tagging for proper nouns
        try:
            tokens = word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            
            for word, tag in pos_tags:
                if tag in ['NNP', 'NNPS']:  # Proper nouns
                    clean = re.sub(r'[^\w\s]', '', word)
                    if clean and len(clean) > 1 and clean not in entities:
                        entities.append(clean)
        except:
            pass
        
        return list(set(entities))  # Remove duplicates
    
    def extract_key_verbs_and_actions(self, text):
        """
        Extract key action verbs and states
        """
        text_lower = text.lower()
        
        # Critical action/state verbs for fact-checking
        key_verbs = {
            'is', 'are', 'was', 'were',  # State of being
            'became', 'become',  # Change of state
            'won', 'lost', 'defeated',  # Competition/election
            'elected', 'appointed', 'selected',  # Official positions
            'resigned', 'retired', 'stepped down',  # Leaving positions
            'announced', 'declared', 'stated',  # Official statements
            'died', 'passed away', 'killed',  # Death
            'married', 'divorced',  # Personal events
            'launched', 'released', 'introduced',  # Product/service
            'banned', 'restricted', 'prohibited',  # Legal actions
            'increased', 'decreased', 'rose', 'fell'  # Quantitative changes
        }
        
        found_verbs = [verb for verb in key_verbs if verb in text_lower]
        
        return found_verbs
    
    def detect_negation_advanced(self, text):
        """
        Advanced negation detection with context
        """
        text_lower = text.lower()
        
        # Expanded negation patterns
        negation_patterns = [
            # Simple negations
            r'\bis\s+not\b', r'\bisn\'t\b', r'\bare\s+not\b', r'\baren\'t\b',
            r'\bwas\s+not\b', r'\bwasn\'t\b', r'\bwere\s+not\b', r'\bweren\'t\b',
            r'\bhas\s+not\b', r'\bhasn\'t\b', r'\bhave\s+not\b', r'\bhaven\'t\b',
            r'\bhad\s+not\b', r'\bhadn\'t\b', r'\bdid\s+not\b', r'\bdidn\'t\b',
            r'\bdo\s+not\b', r'\bdon\'t\b', r'\bdoes\s+not\b', r'\bdoesn\'t\b',
            r'\bwill\s+not\b', r'\bwon\'t\b', r'\bwould\s+not\b', r'\bwouldn\'t\b',
            r'\bcannot\b', r'\bcan\'t\b', r'\bcould\s+not\b', r'\bcouldn\'t\b',
            
            # Context negations
            r'\bnever\b', r'\bneither\b', r'\bnor\b', r'\bnobody\b', r'\bno\s+one\b',
            r'\bnothing\b', r'\bnowhere\b', r'\bno\s+longer\b',
            
            # Implicit negations
            r'\blost\s+the\b', r'\bfailed\s+to\b', r'\brefused\s+to\b',
            r'\bdenied\b', r'\brejected\b'
        ]
        
        negation_count = 0
        negation_positions = []
        
        for pattern in negation_patterns:
            matches = list(re.finditer(pattern, text_lower))
            negation_count += len(matches)
            for match in matches:
                negation_positions.append((match.start(), match.end(), match.group()))
        
        return {
            'has_negation': negation_count > 0,
            'negation_count': negation_count,
            'negation_strength': min(negation_count / 3.0, 1.0),  # Normalized 0-1
            'positions': negation_positions
        }
    
    def extract_temporal_context(self, text):
        """
        Extract time-related information
        """
        text_lower = text.lower()
        
        # Time indicators
        time_patterns = {
            'current': ['currently', 'now', 'today', 'present', 'this year'],
            'past': ['was', 'were', 'yesterday', 'last week', 'last month', 'last year', 
                    'ago', 'previously', 'former', 'ex-'],
            'future': ['will', 'going to', 'next', 'future', 'upcoming', 'soon', 'tomorrow'],
            'ongoing': ['still', 'continues', 'ongoing', 'remains']
        }
        
        detected_time = []
        for time_type, indicators in time_patterns.items():
            if any(indicator in text_lower for indicator in indicators):
                detected_time.append(time_type)
        
        # Extract specific years
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        
        return {
            'temporal_indicators': detected_time,
            'specific_years': years,
            'tense': self._detect_tense(text_lower)
        }
    
    def _detect_tense(self, text):
        """Detect primary verb tense"""
        if any(word in text for word in ['is', 'are', 'am']):
            return 'present'
        elif any(word in text for word in ['was', 'were']):
            return 'past'
        elif any(word in text for word in ['will', 'shall']):
            return 'future'
        return 'unknown'
    
    def extract_claim_components(self, text):
        """
        ENHANCED: Complete claim analysis with all improvements
        """
        components = {
            'entities': self.extract_named_entities(text),
            'verbs': self.extract_key_verbs_and_actions(text),
            'negation': self.detect_negation_advanced(text),
            'temporal': self.extract_temporal_context(text),
            'claim_type': self.identify_claim_type(text),
            'sentiment': self.analyze_sentiment(text)
        }
        
        return components
    
    # ========================================
    # SENTIMENT ANALYSIS
    # ========================================
    
    def analyze_sentiment(self, text):
        """Enhanced sentiment analysis"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # More granular sentiment classification
            if polarity > 0.3:
                sentiment = 'very_positive'
            elif polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.3:
                sentiment = 'very_negative'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'sentiment': sentiment,
                'is_objective': subjectivity < 0.3
            }
        except:
            return {
                'polarity': 0.0,
                'subjectivity': 0.5,
                'sentiment': 'neutral',
                'is_objective': False
            }
    
    # ========================================
    # SEARCH AND RETRIEVAL
    # ========================================
    
    def create_smart_search_query(self, text, components):
        """
        Create optimized search query from claim components
        """
        query_parts = []
        
        # Priority 1: Named entities (most important)
        if components['entities']:
            query_parts.extend(components['entities'][:3])
        
        # Priority 2: Key verbs (action/state)
        if components['verbs']:
            query_parts.extend(components['verbs'][:2])
        
        # Priority 3: Extract important nouns from text
        try:
            tokens = word_tokenize(text)
            pos_tags = nltk.pos_tag(tokens)
            nouns = [word for word, tag in pos_tags 
                    if tag in ['NN', 'NNS'] and word.lower() not in self.stop_words]
            query_parts.extend(nouns[:2])
        except:
            pass
        
        # Remove duplicates and stopwords
        query_parts = [part for part in query_parts 
                      if part.lower() not in self.stop_words and len(part) > 2]
        
        # Limit to 6 words max
        final_query = ' '.join(query_parts[:6])
        
        return final_query if final_query else text[:50]
    
    def search_news(self, query, days_back=30, max_results=20):
        """Search NewsAPI with error handling"""
        if not self.news_api_key or self.news_api_key == 'your_newsapi_key_here':
            return None
        
        try:
            url = f"{self.news_base_url}/everything"
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            params = {
                'apiKey': self.news_api_key,
                'q': query,
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': max_results,
                'from': from_date
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                return articles
            else:
                print(f"[NEWS API] Error {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[NEWS API] Exception: {e}")
            return None
    
    # ========================================
    # CONTENT MATCHING AND VERIFICATION
    # ========================================
    
    def calculate_content_similarity(self, claim_components, article):
        """
        Enhanced similarity calculation with weighted factors
        """
        article_title = article.get('title', '').lower()
        article_desc = article.get('description', '').lower()
        article_text = f"{article_title} {article_desc}"
        
        if not article_text.strip():
            return 0.0
        
        similarity_score = 0.0
        
        # Factor 1: Entity matching (40% weight)
        entity_matches = 0
        for entity in claim_components['entities']:
            if entity.lower() in article_text:
                entity_matches += 1
        
        if claim_components['entities']:
            entity_similarity = entity_matches / len(claim_components['entities'])
            similarity_score += entity_similarity * 0.40
        
        # Factor 2: Verb/action matching (30% weight)
        verb_matches = 0
        for verb in claim_components['verbs']:
            if verb in article_text:
                verb_matches += 1
        
        if claim_components['verbs']:
            verb_similarity = verb_matches / len(claim_components['verbs'])
            similarity_score += verb_similarity * 0.30
        
        # Factor 3: Key term matching (20% weight)
        claim_words = set(word_tokenize(article_text)) - self.stop_words
        article_words = set(word_tokenize(article_text)) - self.stop_words
        
        if article_words:
            word_overlap = len(claim_words & article_words) / len(article_words)
            similarity_score += word_overlap * 0.20
        
        # Factor 4: Title presence (10% bonus if claim entities in title)
        if any(entity.lower() in article_title for entity in claim_components['entities']):
            similarity_score += 0.10
        
        return min(similarity_score, 1.0)
    
    def check_factual_contradiction(self, claim_components, article_text):
        """
        Check if article contradicts the claim's factual assertions
        """
        article_lower = article_text.lower()
        
        # Check for negation contradiction
        claim_has_negation = claim_components['negation']['has_negation']
        
        # Check if article affirms what claim denies (or vice versa)
        contradictions = []
        
        # If claim says "X is NOT Y"
        if claim_has_negation:
            # Check if article says "X is Y" (affirmative)
            for entity in claim_components['entities']:
                for verb in claim_components['verbs']:
                    # Look for affirmative pattern
                    affirmative_pattern = f"{entity.lower()}.*{verb}"
                    if re.search(affirmative_pattern, article_lower):
                        # Check if there's no negation nearby
                        context = re.search(f".{{0,50}}{affirmative_pattern}.{{0,50}}", article_lower)
                        if context:
                            context_text = context.group()
                            # If no negation in context, it's a contradiction
                            if not any(neg in context_text for neg in ['not', "n't", 'no', 'never']):
                                contradictions.append({
                                    'type': 'negation_contradiction',
                                    'entity': entity,
                                    'verb': verb,
                                    'severity': 'high'
                                })
        
        # Check for opposite verbs (won vs lost, etc.)
        opposite_verbs = {
            'won': ['lost', 'defeated'],
            'lost': ['won', 'victory'],
            'elected': ['defeated', 'lost'],
            'appointed': ['removed', 'fired'],
            'is': ['is not', "isn't", 'was not'],
            'became': ['never became', 'failed to become']
        }
        
        for claim_verb in claim_components['verbs']:
            if claim_verb in opposite_verbs:
                opposites = opposite_verbs[claim_verb]
                for opposite in opposites:
                    if opposite in article_lower:
                        contradictions.append({
                            'type': 'opposite_verb',
                            'claim_verb': claim_verb,
                            'article_verb': opposite,
                            'severity': 'high'
                        })
        
        return contradictions
    
    def get_source_credibility_score(self, source_name):
        """
        Rate source credibility (0.0 to 1.0)
        """
        if source_name in self.credible_sources['tier1']:
            return 1.0
        elif source_name in self.credible_sources['tier2']:
            return 0.85
        elif source_name in self.credible_sources['tier3']:
            return 0.70
        else:
            return 0.50  # Unknown sources
    
    def is_article_recent(self, article, days=7):
        """Check if article was published recently"""
        try:
            pub_date = article.get('publishedAt', '')
            if not pub_date:
                return False
            
            article_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            days_old = (datetime.now(article_date.tzinfo) - article_date).days
            
            return days_old <= days
        except:
            return False
    
    # ========================================
    # CONFIDENCE SCORING
    # ========================================
    
    def calculate_confidence_score(self, matches, claim_components, verdict_type):
        """
        Multi-factor confidence calculation
        """
        base_score = 0.50
        
        if not matches:
            return 0.30  # Low confidence when no data
        
        best_match = matches[0]
        
        # Factor 1: Number of supporting sources (up to +0.20)
        if len(matches) >= 5:
            base_score += 0.20
        elif len(matches) >= 3:
            base_score += 0.15
        elif len(matches) >= 2:
            base_score += 0.10
        elif len(matches) >= 1:
            base_score += 0.05
        
        # Factor 2: Content similarity (up to +0.20)
        if best_match['similarity'] >= self.HIGH_CONFIDENCE_SIMILARITY:
            base_score += 0.20
        elif best_match['similarity'] >= self.MIN_SIMILARITY:
            base_score += 0.10 + (best_match['similarity'] - self.MIN_SIMILARITY) * 0.4
        
        # Factor 3: Source credibility (up to +0.15)
        credibility = best_match.get('credibility_score', 0.5)
        base_score += credibility * 0.15
        
        # Factor 4: Recency of articles (up to +0.10)
        recent_count = sum(1 for m in matches if m.get('is_recent', False))
        if recent_count >= 2:
            base_score += 0.10
        elif recent_count >= 1:
            base_score += 0.05
        
        # Factor 5: Contradiction detection (up to +0.15)
        if best_match.get('has_contradictions'):
            if verdict_type == 'false':
                base_score += 0.15  # High confidence it's fake
        
        # Factor 6: Negation handling (up to +0.10)
        if claim_components['negation']['has_negation']:
            if best_match.get('negation_contradiction'):
                base_score += 0.10
        
        # Penalty for opinion-based claims
        if claim_components['claim_type'] == 'opinion':
            base_score -= 0.15
        
        # Penalty for future predictions
        if claim_components['claim_type'] == 'prediction':
            base_score -= 0.20
        
        return max(0.05, min(base_score, 0.98))  # Clamp between 0.05 and 0.98
    
    # ========================================
    # MAIN ANALYSIS AND VERDICT
    # ========================================
    
    def analyze_articles(self, claim_components, articles):
        """
        Analyze articles against claim with enhanced matching
        """
        matches = []
        
        for article in articles:
            article_text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            
            if not article_text.strip():
                continue
            
            # Calculate similarity
            similarity = self.calculate_content_similarity(claim_components, article)
            
            # Skip if below threshold
            if similarity < self.MIN_SIMILARITY:
                continue
            
            # Check for contradictions
            contradictions = self.check_factual_contradiction(claim_components, article_text)
            
            # Get source credibility
            source_name = article.get('source', {}).get('name', 'Unknown')
            credibility = self.get_source_credibility_score(source_name)
            
            # Check recency
            is_recent = self.is_article_recent(article, days=7)
            
            # Analyze article sentiment
            article_sentiment = self.analyze_sentiment(article_text)
            
            match = {
                'title': article.get('title', ''),
                'source': source_name,
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', ''),
                'similarity': similarity,
                'credibility_score': credibility,
                'is_recent': is_recent,
                'article_sentiment': article_sentiment,
                'has_contradictions': len(contradictions) > 0,
                'contradictions': contradictions,
                'negation_contradiction': any(c['type'] == 'negation_contradiction' for c in contradictions)
            }
            
            matches.append(match)
        
        # Sort by similarity * credibility for better ranking
        matches.sort(key=lambda x: x['similarity'] * x['credibility_score'], reverse=True)
        
        return matches
    
    def make_verdict(self, matches, claim_components):
        """
        Make final verdict with enhanced logic
        """
        # CASE 1: No matches found
        if not matches:
            if claim_components['claim_type'] == 'opinion':
                return {
                    'verdict': 'opinion',
                    'prediction': False,  # Opinions aren't "fake news"
                    'confidence': 0.70,
                    'explanation': '💬 This appears to be an opinion or subjective statement rather than a factual claim.',
                    'reason_code': 'OPINION_DETECTED'
                }
            elif claim_components['claim_type'] == 'prediction':
                return {
                    'verdict': 'prediction',
                    'prediction': False,  # Future predictions can't be verified yet
                    'confidence': 0.60,
                    'explanation': '🔮 This is a prediction about future events that cannot be verified yet.',
                    'reason_code': 'FUTURE_PREDICTION'
                }
            else:
                return {
                    'verdict': 'unverifiable',
                    'prediction': True,  # Lean toward skepticism
                    'confidence': 0.65,
                    'explanation': '⚠️ Could not find credible news sources to verify this claim. It may be too new, too localized, or fabricated.',
                    'reason_code': 'NO_SOURCES'
                }
        
        best_match = matches[0]
        
        # CASE 2: Strong contradiction detected
        if best_match['has_contradictions'] and best_match['similarity'] >= 0.60:
            confidence = self.calculate_confidence_score(matches, claim_components, 'false')
            return {
                'verdict': 'false',
                'prediction': True,
                'confidence': confidence,
                'explanation': f"✗ CONTRADICTED: Credible sources including {best_match['source']} report the opposite of this claim. {len(matches)} sources found.",
                'reason_code': 'CONTRADICTION_DETECTED',
                'supporting_sources': matches[:3]
            }
        
        # CASE 3: High similarity + credible sources = VERIFIED
        if (best_match['similarity'] >= self.HIGH_CONFIDENCE_SIMILARITY and 
            best_match['credibility_score'] >= 0.85 and 
            len(matches) >= self.MIN_SOURCES_FOR_VERIFICATION):
            
            confidence = self.calculate_confidence_score(matches, claim_components, 'verified')
            return {
                'verdict': 'verified',
                'prediction': False,
                'confidence': confidence,
                'explanation': f"✓ VERIFIED: Multiple credible sources including {best_match['source']} confirm this claim. {len(matches)} sources found with high similarity ({best_match['similarity']:.0%}).",
                'reason_code': 'HIGH_CONFIDENCE_VERIFICATION',
                'supporting_sources': matches[:3]
            }
        
        # CASE 4: Good similarity + decent sources = LIKELY TRUE
        if (best_match['similarity'] >= 0.60 and 
            best_match['credibility_score'] >= 0.70 and
            len(matches) >= 2):
            
            confidence = self.calculate_confidence_score(matches, claim_components, 'likely_true')
            return {
                'verdict': 'likely_true',
                'prediction': False,
                'confidence': confidence,
                'explanation': f"✓ Likely TRUE: Found supporting evidence from {best_match['source']} and {len(matches)-1} other source(s) with good similarity ({best_match['similarity']:.0%}).",
                'reason_code': 'MODERATE_CONFIDENCE_VERIFICATION',
                'supporting_sources': matches[:2]
            }
        
        # CASE 5: Moderate similarity but conflicting or weak evidence
        if best_match['similarity'] >= self.MIN_SIMILARITY:
            confidence = self.calculate_confidence_score(matches, claim_components, 'uncertain')
            return {
                'verdict': 'uncertain',
                'prediction': None,  # Don't make a guess
                'confidence': confidence,
                'explanation': f"⚠️ UNCERTAIN: Found related content from {len(matches)} source(s) but cannot confirm specific claim details. Manual verification recommended.",
                'reason_code': 'INSUFFICIENT_EVIDENCE',
                'supporting_sources': matches[:2]
            }
        
        # CASE 6: Very weak matches
        return {
            'verdict': 'likely_false',
            'prediction': True,
            'confidence': 0.70,
            'explanation': f"✗ Likely FALSE: Found {len(matches)} related article(s) but with low similarity. Specific claim details not confirmed by credible sources.",
            'reason_code': 'LOW_SIMILARITY',
            'supporting_sources': matches[:1]
        }
    
    def analyze_claim(self, text):
        """
        MAIN ANALYSIS PIPELINE
        """
        print(f"\n{'='*70}")
        print(f"ENHANCED ANALYSIS: {text}")
        print(f"{'='*70}")
        
        # STEP 1: Extract claim components
        components = self.extract_claim_components(text)
        
        print(f"\n[STEP 1] Claim Analysis:")
        print(f"  Type: {components['claim_type'].upper()}")
        print(f"  Entities: {components['entities']}")
        print(f"  Verbs: {components['verbs']}")
        print(f"  Negation: {components['negation']['has_negation']} (strength: {components['negation']['negation_strength']:.2f})")
        print(f"  Temporal: {components['temporal']['tense']} tense")
        print(f"  Sentiment: {components['sentiment']['sentiment']} (polarity: {components['sentiment']['polarity']:.2f})")
        
        # STEP 2: Create optimized search query
        search_query = self.create_smart_search_query(text, components)
        print(f"\n[STEP 2] Search Query: '{search_query}'")
        
        # STEP 3: Search for articles
        articles = self.search_news(search_query, days_back=30, max_results=20)
        
        if articles is None:
            return {
                'text': text,
                'prediction': None,
                'confidence': 0.0,
                'verdict': 'error',
                'explanation': '❌ Unable to access news sources. Check API key configuration.',
                'claim_analysis': components,
                'sources': [],
                'fact_checked': False,
                'timestamp': datetime.now().isoformat()
            }
        
        print(f"\n[STEP 3] Found {len(articles)} articles from NewsAPI")
        
        # STEP 4: Analyze articles
        matches = self.analyze_articles(components, articles)
        print(f"\n[STEP 4] {len(matches)} articles passed similarity threshold (≥{self.MIN_SIMILARITY:.0%})")
        
        if matches:
            best = matches[0]
            print(f"\n  Best Match:")
            print(f"    Source: {best['source']} (credibility: {best['credibility_score']:.2f})")
            print(f"    Similarity: {best['similarity']:.2%}")
            print(f"    Recent: {'Yes' if best['is_recent'] else 'No'}")
            print(f"    Contradictions: {'Yes' if best['has_contradictions'] else 'No'}")
        
        # STEP 5: Make verdict
        verdict_result = self.make_verdict(matches, components)
        
        print(f"\n[STEP 5] VERDICT: {verdict_result['verdict'].upper()}")
        print(f"  Prediction: {'FAKE' if verdict_result['prediction'] else 'REAL' if verdict_result['prediction'] is False else 'UNCERTAIN'}")
        print(f"  Confidence: {verdict_result['confidence']:.2%}")
        print(f"  Reason: {verdict_result['reason_code']}")
        print(f"{'='*70}\n")
        
        # Build final result
        result = {
            'text': text,
            'prediction': verdict_result['prediction'],
            'confidence': verdict_result['confidence'],
            'verdict': verdict_result['verdict'],
            'explanation': verdict_result['explanation'],
            'reason_code': verdict_result['reason_code'],
            'claim_analysis': {
                'type': components['claim_type'],
                'entities': components['entities'],
                'verbs': components['verbs'],
                'has_negation': components['negation']['has_negation'],
                'negation_strength': components['negation']['negation_strength'],
                'sentiment': components['sentiment']['sentiment'],
                'temporal_context': components['temporal']['tense']
            },
            'sources': [
                {
                    'title': m['title'],
                    'source': m['source'],
                    'url': m['url'],
                    'relevance': m['similarity'],
                    'credibility': m['credibility_score'],
                    'published_at': m['published_at']
                }
                for m in matches[:5]  # Top 5 sources
            ],
            'fact_checked': len(matches) > 0,
            'articles_analyzed': len(articles) if articles else 0,
            'relevant_articles': len(matches),
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def predict_single(self, text):
        """
        API-compatible prediction method
        """
        result = self.analyze_claim(text)
        
        # Handle uncertain verdicts for backward compatibility
        if result['prediction'] is None:
            # For uncertain cases, lean toward skepticism
            prediction = True
            confidence = max(result['confidence'] * 0.8, 0.50)
        else:
            prediction = result['prediction']
            confidence = result['confidence']
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'verdict': result['verdict'],
            'explanation': result['explanation'],
            'fact_check': {
                'verified': result['fact_checked'],
                'sources': result['sources'],
                'verdict': result['verdict'],
                'reason_code': result.get('reason_code', 'UNKNOWN')
            },
            'claim_analysis': result['claim_analysis'],
            'ensemble_probability': 1.0 if prediction else 0.0,
            'timestamp': result['timestamp']
        }
    
    def batch_predict(self, texts):
        """
        Batch prediction for multiple claims
        """
        results = []
        for text in texts:
            try:
                result = self.predict_single(text)
                results.append(result)
            except Exception as e:
                print(f"Error processing '{text}': {e}")
                results.append({
                    'prediction': None,
                    'confidence': 0.0,
                    'verdict': 'error',
                    'explanation': f'Error: {str(e)}',
                    'fact_check': {'verified': False, 'sources': []},
                    'claim_analysis': {},
                    'ensemble_probability': 0.5,
                    'timestamp': datetime.now().isoformat()
                })
        
        return results


# ========================================
# NEWS MONITORING CLASS (UNCHANGED)
# ========================================

class NewsAPIMonitor:
    """Monitor latest news with enhanced detection"""
    
    def __init__(self, api_key, detector):
        self.api_key = api_key
        self.detector = detector
        self.base_url = "https://newsapi.org/v2"
    
    def get_top_headlines(self, country='us', category=None, page_size=20):
        """Get top headlines from NewsAPI"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'country': country,
                'pageSize': page_size
            }
            
            if category:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json().get('articles', [])
        except Exception as e:
            print(f"Error fetching headlines: {e}")
            return []
    
    def get_analyzed_headlines(self, country='us', category=None, page_size=20):
        """Get and analyze headlines with enhanced detector"""
        articles = self.get_top_headlines(country, category, page_size)
        
        results = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            if not text.strip():
                continue
            
            try:
                prediction = self.detector.predict_single(text)
                
                results.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'image_url': article.get('urlToImage', ''),
                    'prediction': prediction.get('prediction', False),
                    'confidence': prediction.get('confidence', 0.0),
                    'verdict': prediction.get('verdict', 'unknown'),
                    'explanation': prediction.get('explanation', ''),
                    'analysis_timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error analyzing article: {e}")
                continue
        
        return results
    
    def analyze_articles(self, articles):
        """Analyze a list of articles"""
        results = []
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            if not text.strip():
                continue
            
            try:
                prediction = self.detector.predict_single(text)
                
                results.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'image_url': article.get('urlToImage', ''),
                    'prediction': prediction.get('prediction', False),
                    'confidence': prediction.get('confidence', 0.0),
                    'verdict': prediction.get('verdict', 'unknown'),
                    'explanation': prediction.get('explanation', ''),
                    'claim_type': prediction.get('claim_analysis', {}).get('type', 'unknown'),
                    'fact_checked': prediction.get('fact_check', {}).get('verified', False),
                    'analysis_timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                print(f"Error analyzing article: {e}")
                continue
        
        return results


# ========================================
# USAGE EXAMPLE AND TESTING
# ========================================

if __name__ == "__main__":
    # Test the detector
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_newsapi_key_here')
    
    print("="*70)
    print("ENHANCED FAKE NEWS DETECTOR - TEST SUITE")
    print("="*70)
    
    detector = EnhancedFakeNewsDetector(NEWS_API_KEY)
    
    # Test cases covering various scenarios
    test_cases = [
        {
            'text': 'Narendra Modi is prime minister of India',
            'expected': False,
            'description': 'TRUE factual statement'
        },
        {
            'text': 'Narendra Modi is NOT prime minister of India',
            'expected': True,
            'description': 'FALSE - negation of true fact'
        },
        {
            'text': 'Donald Trump won the 2024 US presidential election',
            'expected': False,
            'description': 'TRUE - recent verified event'
        },
        {
            'text': 'Kamala Harris won the 2024 US presidential election',
            'expected': True,
            'description': 'FALSE - contradicts known fact'
        },
        {
            'text': 'The Earth is flat and NASA is hiding the truth',
            'expected': True,
            'description': 'FALSE - conspiracy theory'
        },
        {
            'text': 'Python is a great programming language for beginners',
            'expected': False,
            'description': 'OPINION - subjective statement'
        },
        {
            'text': 'Scientists will discover life on Mars next year',
            'expected': False,
            'description': 'PREDICTION - future event'
        }
    ]
    
    print("\nRunning test cases...\n")
    
    results = []
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {case['description']}")
        print(f"Input: '{case['text']}'")
        
        try:
            result = detector.predict_single(case['text'])
            
            prediction = result['prediction']
            expected = case['expected']
            
            # Handle None predictions (uncertain cases)
            if prediction is None:
                status = "⚠️ UNCERTAIN"
                is_correct = "N/A"
            else:
                is_correct = prediction == expected
                status = "✓ PASS" if is_correct else "✗ FAIL"
            
            print(f"Expected: {'FAKE' if expected else 'REAL'}")
            print(f"Predicted: {'FAKE' if prediction else 'REAL' if prediction is False else 'UNCERTAIN'}")
            print(f"Verdict: {result['verdict']}")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Status: {status}")
            
            results.append({
                'case': case['description'],
                'status': status,
                'correct': is_correct if is_correct != "N/A" else None,
                'confidence': result['confidence']
            })
            
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                'case': case['description'],
                'status': "✗ ERROR",
                'correct': False,
                'confidence': 0.0
            })
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if '✓' in r['status'])
    failed = sum(1 for r in results if '✗' in r['status'])
    uncertain = sum(1 for r in results if '⚠️' in r['status'])
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Uncertain: {uncertain}")
    
    if len(results) > 0:
        accuracy = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"Accuracy: {accuracy:.1f}%")
    
    print("\nDetailed Results:")
    for r in results:
        print(f"  {r['status']} - {r['case']} (confidence: {r['confidence']:.2%})")
    
    print("\n" + "="*70)