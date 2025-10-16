import json
import re
from typing import Dict, List, Tuple

class BehavioralAnalyzer:
    def __init__(self):
        self.openai_api_key = "YOUR_OPENAI_API_KEY"  # Replace with actual key
        
    def analyze_responses(self, mcq_answers: Dict, written_responses: Dict) -> Tuple[int, str]:
        """
        Analyze behavioral responses using AI-powered analysis
        Returns: (score, detailed_analysis)
        """
        try:
            # Calculate MCQ scores
            mcq_score = self._analyze_mcq_responses(mcq_answers)
            
            # Analyze written responses with AI
            written_analysis = self._analyze_written_responses_ai(written_responses)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(mcq_score, written_analysis)
            
            # Generate detailed analysis
            detailed_analysis = self._generate_detailed_analysis(mcq_score, written_analysis)
            
            return overall_score, detailed_analysis
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            # Fallback to simple analysis
            return self._fallback_analysis(mcq_answers, written_responses)
    
    def _analyze_mcq_responses(self, mcq_answers: Dict) -> Dict[str, int]:
        """Analyze MCQ responses based on predefined weights"""
        category_scores = {
            'work_ethics': 0,
            'leadership': 0,
            'problem_solving': 0,
            'communication': 0,
            'cultural_fit': 0
        }
        
        # Load question weights
        with open('behavioral_questions.json', 'r') as f:
            questions = json.load(f)
        
        mcq_questions = [q for q in questions if q['type'] == 'mcq']
        
        for question in mcq_questions:
            q_id = str(question['id'])
            if q_id in mcq_answers:
                answer = mcq_answers[q_id]
                category = question['category']
                weight = question['weights'].get(answer, 0)
                category_scores[category] += weight
        
        return category_scores
    
    def _analyze_written_responses_ai(self, written_responses: Dict) -> Dict:
        """Analyze written responses using AI"""
        analysis_results = {}
        
        for q_id, response in written_responses.items():
            try:
                # Use OpenAI API for analysis
                analysis = self._call_openai_api(q_id, response)
                analysis_results[q_id] = analysis
            except Exception as e:
                print(f"OpenAI API error for question {q_id}: {e}")
                # Fallback to keyword analysis
                analysis_results[q_id] = self._analyze_text_keywords(q_id, response)
        
        return analysis_results
    
    def _call_openai_api(self, question_id: str, response: str) -> Dict:
        """Call OpenAI API for text analysis"""
        # This would be the actual OpenAI API call
        # For now, we'll simulate it with advanced keyword analysis
        
        prompt = f"""
        Analyze this behavioral response for a job candidate:
        
        Question ID: {question_id}
        Response: {response}
        
        Rate on scale 1-10 for:
        1. Relevance to question
        2. Professional communication
        3. Problem-solving approach
        4. Cultural fit indicators
        5. Specificity and detail
        
        Provide overall score (1-100) and brief reasoning.
        """
        
        # Simulated AI response (replace with actual OpenAI API call)
        ai_score = self._simulate_ai_analysis(response)
        ai_reasoning = self._generate_ai_reasoning(response)
        
        return {
            'score': ai_score,
            'reasoning': ai_reasoning,
            'relevance': self._check_relevance(response),
            'professionalism': self._check_professionalism(response),
            'specificity': self._check_specificity(response)
        }
    
    def _simulate_ai_analysis(self, text: str) -> int:
        """Simulate AI analysis with advanced keyword and pattern matching"""
        score = 0
        
        # Length analysis
        word_count = len(text.split())
        if word_count > 50:
            score += 30
        elif word_count > 30:
            score += 25
        elif word_count > 15:
            score += 20
        else:
            score += 10
        
        # Professional language detection
        professional_patterns = [
            r'\b(analyze|implement|collaborate|strategic|initiative)\b',
            r'\b(experience|approach|solution|challenge|outcome)\b',
            r'\b(team|project|communication|leadership|management)\b'
        ]
        
        for pattern in professional_patterns:
            matches = len(re.findall(pattern, text.lower()))
            score += matches * 5
        
        # Positive sentiment indicators
        positive_words = ['success', 'achieved', 'improved', 'resolved', 'learned', 'developed']
        positive_count = sum(1 for word in positive_words if word in text.lower())
        score += positive_count * 8
        
        # Specific examples detection
        example_indicators = ['for example', 'specifically', 'in one case', 'when i', 'i remember']
        if any(indicator in text.lower() for indicator in example_indicators):
            score += 15
        
        # Red flags detection
        red_flags = ['blame', 'fault', 'hate', 'terrible', 'awful', 'never']
        if any(flag in text.lower() for flag in red_flags):
            score -= 20
        
        return min(100, max(0, score))
    
    def _generate_ai_reasoning(self, text: str) -> str:
        """Generate AI-style reasoning for the analysis"""
        word_count = len(text.split())
        
        if word_count > 50:
            length_feedback = "Detailed and comprehensive response"
        elif word_count > 30:
            length_feedback = "Good level of detail"
        elif word_count > 15:
            length_feedback = "Adequate response length"
        else:
            length_feedback = "Response could be more detailed"
        
        # Check for specific examples
        if any(indicator in text.lower() for indicator in ['for example', 'specifically', 'when i']):
            example_feedback = "Includes specific examples"
        else:
            example_feedback = "Could benefit from more specific examples"
        
        # Check professionalism
        if any(word in text.lower() for word in ['analyze', 'implement', 'collaborate', 'strategic']):
            professional_feedback = "Uses professional language"
        else:
            professional_feedback = "Language is appropriate"
        
        return f"{length_feedback}. {example_feedback}. {professional_feedback}."
    
    def _check_relevance(self, text: str) -> int:
        """Check how relevant the response is to behavioral questions"""
        behavioral_keywords = [
            'team', 'leadership', 'communication', 'problem', 'solution',
            'experience', 'situation', 'challenge', 'outcome', 'learned'
        ]
        
        keyword_count = sum(1 for keyword in behavioral_keywords if keyword in text.lower())
        return min(10, keyword_count)
    
    def _check_professionalism(self, text: str) -> int:
        """Check professionalism level"""
        professional_score = 5  # Base score
        
        # Check for professional language
        if any(word in text.lower() for word in ['analyze', 'implement', 'collaborate', 'strategic']):
            professional_score += 3
        
        # Check for appropriate tone
        if not any(word in text.lower() for word in ['awesome', 'cool', 'dude', 'gonna']):
            professional_score += 2
        
        return min(10, professional_score)
    
    def _check_specificity(self, text: str) -> int:
        """Check how specific and detailed the response is"""
        specificity_score = 5  # Base score
        
        # Check for specific examples
        if any(indicator in text.lower() for indicator in ['for example', 'specifically', 'when i', 'i remember']):
            specificity_score += 3
        
        # Check for concrete details
        if any(word in text.lower() for word in ['project', 'team', 'deadline', 'result', 'outcome']):
            specificity_score += 2
        
        return min(10, specificity_score)
    
    def _analyze_text_keywords(self, question_id: str, response: str) -> Dict:
        """Fallback keyword analysis"""
        with open('behavioral_questions.json', 'r') as f:
            questions = json.load(f)
        
        question = next((q for q in questions if str(q['id']) == question_id), None)
        if not question:
            return {'score': 50, 'reasoning': 'Unable to analyze'}
        
        expected_keywords = question.get('expected_keywords', [])
        min_words = question.get('min_words', 20)
        
        score = 0
        word_count = len(response.split())
        
        # Length check
        if word_count >= min_words:
            score += 40
        elif word_count >= min_words * 0.7:
            score += 30
        else:
            score += 20
        
        # Keyword matching
        response_lower = response.lower()
        keyword_matches = sum(1 for keyword in expected_keywords if keyword in response_lower)
        score += keyword_matches * 10
        
        return {
            'score': min(100, score),
            'reasoning': f"Response length: {word_count} words, Keyword matches: {keyword_matches}",
            'relevance': keyword_matches,
            'professionalism': 7,
            'specificity': min(10, word_count // 5)
        }
    
    def _calculate_overall_score(self, mcq_scores: Dict, written_analysis: Dict) -> int:
        """Calculate overall behavioral score"""
        # Average MCQ scores
        mcq_avg = sum(mcq_scores.values()) / len(mcq_scores) if mcq_scores else 0
        
        # Average written scores
        written_scores = [analysis['score'] for analysis in written_analysis.values()]
        written_avg = sum(written_scores) / len(written_scores) if written_scores else 0
        
        # Weighted combination (60% MCQ, 40% Written)
        overall_score = (mcq_avg * 0.6) + (written_avg * 0.4)
        
        return int(overall_score)
    
    def _generate_detailed_analysis(self, mcq_scores: Dict, written_analysis: Dict) -> str:
        """Generate detailed analysis report"""
        analysis_parts = []
        
        # MCQ Analysis
        analysis_parts.append("MULTIPLE CHOICE ANALYSIS:")
        for category, score in mcq_scores.items():
            level = "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Improvement"
            analysis_parts.append(f"- {category.replace('_', ' ').title()}: {score}/100 ({level})")
        
        # Written Analysis
        analysis_parts.append("\nWRITTEN RESPONSE ANALYSIS:")
        for q_id, analysis in written_analysis.items():
            analysis_parts.append(f"- Question {q_id}: {analysis['score']}/100")
            analysis_parts.append(f"  Reasoning: {analysis['reasoning']}")
        
        # Overall Assessment
        overall_score = self._calculate_overall_score(mcq_scores, written_analysis)
        if overall_score >= 80:
            recommendation = "STRONG CANDIDATE - Recommended for hire"
        elif overall_score >= 60:
            recommendation = "GOOD CANDIDATE - Consider for hire"
        else:
            recommendation = "NEEDS IMPROVEMENT - Consider additional evaluation"
        
        analysis_parts.append(f"\nOVERALL ASSESSMENT:")
        analysis_parts.append(f"Score: {overall_score}/100")
        analysis_parts.append(f"Recommendation: {recommendation}")
        
        return "\n".join(analysis_parts)
    
    def _fallback_analysis(self, mcq_answers: Dict, written_responses: Dict) -> Tuple[int, str]:
        """Fallback analysis when AI fails"""
        mcq_score = self._analyze_mcq_responses(mcq_answers)
        written_analysis = {}
        
        for q_id, response in written_responses.items():
            written_analysis[q_id] = self._analyze_text_keywords(q_id, response)
        
        overall_score = self._calculate_overall_score(mcq_score, written_analysis)
        detailed_analysis = self._generate_detailed_analysis(mcq_score, written_analysis)
        
        return overall_score, detailed_analysis
