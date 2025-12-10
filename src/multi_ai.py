"""
Prometheus V7.3 - Multi-AI Analysis Engine
Uses premium AI models for deep match analysis.
- Gemini 2.5 Pro (for complex reasoning)
- GPT-4o (for strategic analysis)  
- Claude Opus 4 (for comprehensive reports)
"""
import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import pytz

SP_TZ = pytz.timezone('America/Sao_Paulo')


class AIProvider:
    """Base class for AI providers."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def analyze(self, prompt: str, system: str = None) -> Dict:
        raise NotImplementedError


class OpenRouterProvider(AIProvider):
    """OpenRouter API for accessing multiple AI models."""
    
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Premium models for analysis
    MODELS = {
        "gemini": "google/gemini-2.5-pro-preview",
        "gpt4": "openai/gpt-4o",
        "opus": "anthropic/claude-opus-4",
        "sonnet": "anthropic/claude-sonnet-4",  # Cost-effective fallback
        "flash": "google/gemini-2.0-flash-001"  # Fast & cheap for simple tasks
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://prometheus-dota2.streamlit.app",
            "X-Title": "Prometheus V7 Dota2 Analyzer"
        }
    
    async def call_model(
        self, 
        model: str, 
        prompt: str, 
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict:
        """Call a specific model via OpenRouter."""
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.MODELS.get(model, model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "model": model,
                            "content": data["choices"][0]["message"]["content"],
                            "usage": data.get("usage", {})
                        }
                    else:
                        error = await response.text()
                        return {
                            "success": False,
                            "model": model,
                            "error": f"API error {response.status}: {error}"
                        }
        except Exception as e:
            return {
                "success": False,
                "model": model,
                "error": str(e)
            }


class MultiAIAnalyzer:
    """
    Multi-model AI analyzer for Dota 2 matches.
    Uses consensus from multiple premium models for important analysis.
    """
    
    SYSTEM_PROMPT = """You are an expert Dota 2 analyst for the Prometheus betting analysis system.
You specialize in professional Dota 2 matches, particularly DreamLeague and other tier 1 tournaments.

Your analysis should cover:
1. Team form and recent performance
2. Head-to-head historical data
3. Draft tendencies and hero pools
4. Player individual performance
5. Meta relevance and patch adaptations
6. Map/objective control patterns
7. Game duration tendencies

Provide analysis in structured JSON format when requested.
Be precise with statistics and confident in predictions while acknowledging uncertainty.
Use Brazilian Portuguese for final reports.
"""
    
    def __init__(self):
        self.provider = OpenRouterProvider()
    
    async def analyze_match(
        self,
        team_a: str,
        team_b: str,
        match_data: Dict = None,
        format_type: str = "Bo3"
    ) -> Dict:
        """
        Perform comprehensive match analysis using multiple AI models.
        
        For important analysis (pre-match reports), uses:
        - Gemini 2.5 Pro: Strategic and meta analysis
        - GPT-4o: Statistical patterns and predictions
        - Claude Opus: Comprehensive synthesis
        
        Returns consensus analysis.
        """
        
        prompt = self._build_analysis_prompt(team_a, team_b, match_data, format_type)
        
        # Run premium models in parallel for important analysis
        tasks = [
            self.provider.call_model("gemini", prompt, self.SYSTEM_PROMPT),
            self.provider.call_model("gpt4", prompt, self.SYSTEM_PROMPT),
            self.provider.call_model("opus", prompt, self.SYSTEM_PROMPT)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        analyses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                continue
            if result.get("success"):
                analyses.append({
                    "model": result["model"],
                    "content": result["content"],
                    "usage": result.get("usage", {})
                })
        
        # Build consensus
        consensus = self._build_consensus(analyses, team_a, team_b)
        
        return {
            "match": f"{team_a} vs {team_b}",
            "format": format_type,
            "timestamp": datetime.now(SP_TZ).isoformat(),
            "models_used": [a["model"] for a in analyses],
            "consensus": consensus,
            "individual_analyses": analyses
        }
    
    async def quick_analysis(
        self,
        team_a: str,
        team_b: str,
        match_data: Dict = None
    ) -> Dict:
        """Quick analysis using cost-effective model (Gemini Flash)."""
        
        prompt = self._build_quick_prompt(team_a, team_b, match_data)
        
        result = await self.provider.call_model(
            "flash", 
            prompt, 
            self.SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=1500
        )
        
        if result.get("success"):
            return {
                "success": True,
                "match": f"{team_a} vs {team_b}",
                "analysis": result["content"],
                "model": "flash"
            }
        return {"success": False, "error": result.get("error")}
    
    async def analyze_draft(
        self,
        radiant_picks: List[str],
        dire_picks: List[str],
        radiant_bans: List[str] = None,
        dire_bans: List[str] = None
    ) -> Dict:
        """Analyze draft composition and predict game dynamics."""
        
        prompt = f"""Analyze this Dota 2 draft:

RADIANT PICKS: {', '.join(radiant_picks)}
DIRE PICKS: {', '.join(dire_picks)}

{f"RADIANT BANS: {', '.join(radiant_bans)}" if radiant_bans else ""}
{f"DIRE BANS: {', '.join(dire_bans)}" if dire_bans else ""}

Provide analysis in JSON format:
{{
    "draft_winner": "radiant" or "dire",
    "draft_advantage": 1-10 scale,
    "win_condition_radiant": "description",
    "win_condition_dire": "description",
    "timing": "early/mid/late game advantage",
    "key_matchups": ["lane matchup descriptions"],
    "predicted_duration": "short (<30min) / medium (30-45min) / long (>45min)",
    "radiant_win_probability": 0-100,
    "analysis_pt": "Análise completa em português"
}}
"""
        
        # Use Gemini for draft analysis (good at strategic reasoning)
        result = await self.provider.call_model(
            "gemini",
            prompt,
            self.SYSTEM_PROMPT,
            temperature=0.3
        )
        
        if result.get("success"):
            try:
                # Try to parse JSON from response
                content = result["content"]
                # Find JSON block
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                analysis = json.loads(content)
                return {"success": True, "analysis": analysis}
            except json.JSONDecodeError:
                return {"success": True, "analysis": {"raw": result["content"]}}
        
        return {"success": False, "error": result.get("error")}
    
    def _build_analysis_prompt(
        self,
        team_a: str,
        team_b: str,
        match_data: Dict,
        format_type: str
    ) -> str:
        """Build comprehensive analysis prompt."""
        
        data_section = ""
        if match_data:
            data_section = f"""
DADOS DISPONÍVEIS:
- Head-to-Head: {match_data.get('h2h', 'N/A')}
- Form {team_a}: {match_data.get('form_a', 'N/A')}
- Form {team_b}: {match_data.get('form_b', 'N/A')}
- Hero Pool {team_a}: {match_data.get('heroes_a', 'N/A')}
- Hero Pool {team_b}: {match_data.get('heroes_b', 'N/A')}
- Recent Matches: {match_data.get('recent_matches', 'N/A')}
"""
        
        return f"""ANÁLISE PRÉ-PARTIDA DETALHADA

PARTIDA: {team_a} vs {team_b}
FORMATO: {format_type}
TORNEIO: DreamLeague Season 27

{data_section}

Forneça uma análise completa em JSON:
{{
    "prediction": {{
        "winner": "nome do time",
        "confidence": 0-100,
        "score_prediction": "2-1" ou similar para Bo3
    }},
    "key_factors": [
        "fator 1",
        "fator 2",
        "fator 3"
    ],
    "h2h_analysis": "análise do histórico",
    "form_analysis": {{
        "team_a": "análise form",
        "team_b": "análise form"
    }},
    "draft_tendencies": {{
        "team_a": ["heróis/estratégias prováveis"],
        "team_b": ["heróis/estratégias prováveis"]
    }},
    "game_predictions": {{
        "expected_duration": "curta/média/longa",
        "likely_first_blood": "time",
        "tempo_advantage": "time"
    }},
    "betting_insight": {{
        "recommendation": "bet/skip/wait",
        "edge": "descrição da edge se houver",
        "risk_level": "baixo/médio/alto"
    }},
    "full_analysis_pt": "Análise completa em português brasileiro (2-3 parágrafos)"
}}
"""
    
    def _build_quick_prompt(
        self,
        team_a: str,
        team_b: str,
        match_data: Dict = None
    ) -> str:
        """Build quick analysis prompt."""
        
        return f"""Análise rápida: {team_a} vs {team_b}

Forneça:
1. Favorito e confiança (%)
2. 3 fatores-chave
3. Recomendação de aposta (1 linha)

Responda em português, máximo 200 palavras."""
    
    def _build_consensus(
        self,
        analyses: List[Dict],
        team_a: str,
        team_b: str
    ) -> Dict:
        """Build consensus from multiple model analyses."""
        
        if not analyses:
            return {"error": "No successful analyses"}
        
        # Extract predictions from each model
        predictions = []
        for analysis in analyses:
            content = analysis.get("content", "")
            # Simple extraction - in production, parse JSON properly
            if team_a.lower() in content.lower():
                predictions.append(team_a)
            elif team_b.lower() in content.lower():
                predictions.append(team_b)
        
        # Determine consensus winner
        if predictions:
            from collections import Counter
            winner_counts = Counter(predictions)
            consensus_winner = winner_counts.most_common(1)[0][0]
            agreement = winner_counts[consensus_winner] / len(analyses) * 100
        else:
            consensus_winner = "Uncertain"
            agreement = 0
        
        return {
            "predicted_winner": consensus_winner,
            "model_agreement": f"{agreement:.0f}%",
            "models_agreeing": len([p for p in predictions if p == consensus_winner]),
            "total_models": len(analyses)
        }


# Convenience functions
async def analyze_upcoming_match(team_a: str, team_b: str, data: Dict = None) -> Dict:
    """Analyze an upcoming match with multi-AI consensus."""
    analyzer = MultiAIAnalyzer()
    return await analyzer.analyze_match(team_a, team_b, data)


async def quick_prediction(team_a: str, team_b: str) -> Dict:
    """Get quick prediction using cost-effective model."""
    analyzer = MultiAIAnalyzer()
    return await analyzer.quick_analysis(team_a, team_b)


async def analyze_live_draft(
    radiant_picks: List[str],
    dire_picks: List[str],
    radiant_bans: List[str] = None,
    dire_bans: List[str] = None
) -> Dict:
    """Analyze live draft composition."""
    analyzer = MultiAIAnalyzer()
    return await analyzer.analyze_draft(
        radiant_picks, dire_picks,
        radiant_bans, dire_bans
    )


# Sync wrappers for Streamlit
def sync_analyze_match(team_a: str, team_b: str, data: Dict = None) -> Dict:
    """Synchronous wrapper for match analysis."""
    return asyncio.run(analyze_upcoming_match(team_a, team_b, data))


def sync_quick_prediction(team_a: str, team_b: str) -> Dict:
    """Synchronous wrapper for quick prediction."""
    return asyncio.run(quick_prediction(team_a, team_b))


def sync_analyze_draft(
    radiant_picks: List[str],
    dire_picks: List[str],
    radiant_bans: List[str] = None,
    dire_bans: List[str] = None
) -> Dict:
    """Synchronous wrapper for draft analysis."""
    return asyncio.run(analyze_live_draft(
        radiant_picks, dire_picks,
        radiant_bans, dire_bans
    ))
