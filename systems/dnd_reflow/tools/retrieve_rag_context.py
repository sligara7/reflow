#!/usr/bin/env python3
"""
Retrieve context using RAG embeddings for reflow workflows.

This tool performs semantic search over embedded knowledge bases to retrieve
relevant context based on queries, current state, or degradation signals.

Usage:
    python3 retrieve_rag_context.py <system_path> --query "your query" [--strategy <strategy_name>]
"""

import json
import sys
import pickle
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import argparse

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
except ImportError as e:
    print(f"ERROR: Required dependencies not installed: {e}")
    print("Install with: pip install sentence-transformers faiss-cpu numpy")
    sys.exit(1)


class RAGContextRetriever:
    """Retrieve relevant context using RAG embeddings."""
    
    def __init__(self, system_path: str, config_path: str = None):
        self.system_path = Path(system_path).resolve()
        self.reflow_root = self._find_reflow_root()
        
        # Load RAG configuration
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.system_path / "context" / "rag_context_config.json"
        
        if not self.config_path.exists():
            print(f"ERROR: RAG config not found at {self.config_path}")
            sys.exit(1)
        
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
            self.config = config_data.get('rag_context_configuration', config_data)
        
        # Initialize embedding model
        model_name = self.config['embedding_configuration']['model']
        self.model = SentenceTransformer(model_name)
        
        # Load embeddings
        self.embeddings_dir = self.system_path / self.config['embedding_configuration']['storage_path']
        self.knowledge_bases = {}
        self._load_knowledge_bases()
        
        # Metrics tracking
        self.metrics = {
            'queries_executed': 0,
            'total_retrieval_time_ms': 0,
            'average_relevance_score': 0,
            'degradation_detections': 0
        }
    
    def _find_reflow_root(self) -> Path:
        """Find the reflow root directory."""
        current = self.system_path
        while current != current.parent:
            if (current / "tools").exists() and (current / "templates").exists():
                return current
            current = current.parent
        raise RuntimeError("Could not find reflow root")
    
    def _load_knowledge_bases(self):
        """Load all embedded knowledge bases."""
        print(f"Loading knowledge bases from {self.embeddings_dir}")
        
        for kb_config in self.config['knowledge_bases']:
            kb_name = kb_config['name']
            embeddings_file = self.embeddings_dir / kb_config['embeddings_file']
            metadata_file = self.embeddings_dir / kb_config['metadata_file']
            
            if not embeddings_file.exists():
                print(f"WARNING: Embeddings not found for {kb_name}, skipping")
                continue
            
            with open(embeddings_file, 'rb') as f:
                embeddings_data = pickle.load(f)
            
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            self.knowledge_bases[kb_name] = {
                'config': kb_config,
                'index': embeddings_data['index'],
                'embeddings': embeddings_data['embeddings'],
                'chunks': embeddings_data['chunks'],
                'metadata': metadata
            }
            
            print(f"  Loaded {kb_name}: {metadata['num_chunks']} chunks")
    
    def _query_knowledge_base(
        self, 
        kb_name: str, 
        query: str, 
        top_k: int = 5, 
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Query a specific knowledge base."""
        if kb_name not in self.knowledge_bases:
            return []
        
        kb = self.knowledge_bases[kb_name]
        
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search
        similarities, indices = kb['index'].search(query_embedding, top_k)
        
        # Filter by minimum similarity
        results = []
        for sim, idx in zip(similarities[0], indices[0]):
            if sim >= min_similarity:
                chunk = kb['chunks'][idx].copy()
                chunk['similarity'] = float(sim)
                chunk['kb_name'] = kb_name
                chunk['priority'] = kb['config'].get('priority', 'MEDIUM')
                results.append(chunk)
        
        return results
    
    def retrieve_by_strategy(self, strategy_name: str, context_vars: Dict[str, Any] = None) -> Dict[str, Any]:
        """Retrieve context using a predefined strategy."""
        if context_vars is None:
            context_vars = self._load_current_context()
        
        strategies = self.config.get('retrieval_strategies', {})
        if strategy_name not in strategies:
            print(f"ERROR: Strategy '{strategy_name}' not found")
            return {}
        
        strategy = strategies[strategy_name]
        print(f"\nExecuting retrieval strategy: {strategy_name}")
        print(f"Description: {strategy.get('description')}")
        
        all_results = {
            'strategy': strategy_name,
            'timestamp': datetime.now().isoformat(),
            'context_vars': context_vars,
            'critical_context': [],
            'high_priority_context': [],
            'medium_priority_context': [],
            'always_included': []
        }
        
        # Execute queries
        for query_config in strategy.get('queries', []):
            query_template = query_config['query_template']
            
            # Substitute variables
            query = query_template.format(**context_vars)
            
            print(f"\n  Query: {query}")
            
            # Query each knowledge base
            for kb_name in query_config.get('knowledge_bases', []):
                results = self._query_knowledge_base(
                    kb_name,
                    query,
                    top_k=query_config.get('top_k', 5),
                    min_similarity=query_config.get('min_similarity', 0.7)
                )
                
                print(f"    {kb_name}: {len(results)} matches")
                
                # Categorize by priority
                for result in results:
                    priority = result.get('priority', 'MEDIUM')
                    if priority == 'CRITICAL':
                        all_results['critical_context'].append(result)
                    elif priority == 'HIGH':
                        all_results['high_priority_context'].append(result)
                    else:
                        all_results['medium_priority_context'].append(result)
        
        # Add always-included context
        always_include = strategy.get('always_include', [])
        for context_ref in always_include:
            context_data = self._resolve_context_reference(context_ref, context_vars)
            if context_data:
                all_results['always_included'].append(context_data)
        
        # Sort by relevance within each priority
        all_results['critical_context'].sort(key=lambda x: x.get('similarity', 0), reverse=True)
        all_results['high_priority_context'].sort(key=lambda x: x.get('similarity', 0), reverse=True)
        all_results['medium_priority_context'].sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        # Apply token budget
        all_results = self._apply_token_budget(all_results)
        
        # Update metrics
        self.metrics['queries_executed'] += len(strategy.get('queries', []))
        
        return all_results
    
    def _load_current_context(self) -> Dict[str, Any]:
        """Load current workflow context from tracking files."""
        context = {
            'system_name': self.system_path.name,
            'current_step': 'unknown',
            'current_substep': 'unknown',
            'working_directory': str(self.system_path)
        }
        
        # Load from working_memory.json
        working_memory_path = self.system_path / "context" / "working_memory.json"
        if working_memory_path.exists():
            with open(working_memory_path, 'r') as f:
                memory = json.load(f)
                context['system_name'] = memory.get('system_name', context['system_name'])
        
        # Load from step_progress_tracker.json
        tracker_path = self.system_path / "context" / "step_progress_tracker.json"
        if tracker_path.exists():
            with open(tracker_path, 'r') as f:
                tracker = json.load(f)
                context['current_step'] = tracker.get('current_step', context['current_step'])
                context['current_substep'] = tracker.get('current_substep', context['current_substep'])
        
        return context
    
    def _resolve_context_reference(self, ref: str, context_vars: Dict) -> Dict[str, Any]:
        """Resolve a context reference like 'CRITICAL_BEHAVIORAL_RULES' or 'working_memory.json'."""
        # File reference
        if ref.endswith('.json') or ref.endswith('.md'):
            file_path = self.system_path / "context" / ref
            if file_path.exists():
                with open(file_path, 'r') as f:
                    if ref.endswith('.json'):
                        content = json.load(f)
                        text = json.dumps(content, indent=2)
                    else:
                        text = f.read()
                
                return {
                    'id': ref,
                    'text': text,
                    'type': 'file_reference',
                    'priority': 'CRITICAL',
                    'similarity': 1.0
                }
        
        # Section reference - search in decision_flow
        if '.' in ref:
            # Nested section like "CRITICAL_BEHAVIORAL_RULES.NEVER_GENERATE_REPORTS"
            parts = ref.split('.')
            decision_flow_path = self.reflow_root / "decision_flow.json"
            
            if decision_flow_path.exists():
                with open(decision_flow_path, 'r') as f:
                    data = json.load(f)
                
                current = data
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return None
                
                return {
                    'id': ref,
                    'text': json.dumps(current, indent=2) if isinstance(current, (dict, list)) else str(current),
                    'type': 'section_reference',
                    'priority': 'CRITICAL',
                    'similarity': 1.0
                }
        
        # Simple section reference from context vars
        if ref in context_vars:
            return {
                'id': ref,
                'text': str(context_vars[ref]),
                'type': 'context_var',
                'priority': 'CRITICAL',
                'similarity': 1.0
            }
        
        return None
    
    def _apply_token_budget(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply token budget constraints to retrieval results."""
        budget_config = self.config['context_prioritization']['token_budget_management']
        priority_levels = self.config['context_prioritization']['priority_levels']
        
        # Estimate tokens (rough: ~4 chars per token)
        def estimate_tokens(text: str) -> int:
            return len(text) // 4
        
        # Apply budget per priority
        for key, priority_name in [
            ('critical_context', 'CRITICAL'),
            ('high_priority_context', 'HIGH'),
            ('medium_priority_context', 'MEDIUM')
        ]:
            max_budget = priority_levels[priority_name]['max_token_budget']
            current_tokens = 0
            kept_results = []
            
            for result in results[key]:
                result_tokens = estimate_tokens(result['text'])
                if current_tokens + result_tokens <= max_budget:
                    kept_results.append(result)
                    current_tokens += result_tokens
                else:
                    break  # Budget exceeded
            
            results[key] = kept_results
        
        return results
    
    def format_context_for_injection(self, results: Dict[str, Any]) -> str:
        """Format retrieved context for LLM prompt injection."""
        injection_template = self.config['injection_mechanism']['injection_points'][0]['template']
        formatting = self.config['injection_mechanism']['formatting_rules']
        
        # Format each priority level
        def format_section(items: List[Dict], highlight: str = "") -> str:
            if not items:
                return ""
            
            lines = []
            for item in items:
                lines.append(f"\n{highlight} {item['id']} (similarity: {item.get('similarity', 1.0):.2f})")
                lines.append(f"```json")
                lines.append(item['text'][:1000])  # Truncate if too long
                lines.append(f"```\n")
            return "\n".join(lines)
        
        critical = format_section(
            results['critical_context'] + results['always_included'],
            formatting['highlight_critical']
        )
        high = format_section(results['high_priority_context'])
        medium = format_section(results['medium_priority_context'])
        
        formatted = injection_template.format(
            critical_context=critical or "None",
            high_priority_context=high or "None",
            medium_priority_context=medium or "None"
        )
        
        return formatted
    
    def detect_degradation(self, agent_output: str) -> List[str]:
        """Detect degradation signals in agent output."""
        detected_signals = []
        
        degradation_config = self.config.get('degradation_detection', {})
        if not degradation_config.get('monitoring_enabled', True):
            return detected_signals
        
        for signal_config in degradation_config.get('signal_patterns', []):
            signal_name = signal_config['signal']
            patterns = signal_config['detection_patterns']
            
            for pattern in patterns:
                if re.search(pattern, agent_output, re.IGNORECASE):
                    detected_signals.append(signal_name)
                    self.metrics['degradation_detections'] += 1
                    print(f"⚠️  Degradation detected: {signal_name}")
                    break
        
        return detected_signals
    
    def retrieve_for_degradation(self, detected_signals: List[str]) -> Dict[str, Any]:
        """Retrieve targeted context for detected degradation signals."""
        print(f"\nRetrieving corrective context for: {detected_signals}")
        
        degradation_config = self.config.get('degradation_detection', {})
        all_target_sections = []
        
        # Collect target sections for all detected signals
        for signal_config in degradation_config.get('signal_patterns', []):
            if signal_config['signal'] in detected_signals:
                all_target_sections.extend(signal_config.get('target_sections', []))
        
        # Retrieve the targeted sections
        context_vars = self._load_current_context()
        results = {
            'strategy': 'degradation_correction',
            'timestamp': datetime.now().isoformat(),
            'detected_signals': detected_signals,
            'critical_context': [],
            'always_included': []
        }
        
        for section_ref in all_target_sections:
            context_data = self._resolve_context_reference(section_ref, context_vars)
            if context_data:
                results['always_included'].append(context_data)
        
        return results
    
    def save_metrics(self):
        """Save retrieval metrics."""
        metrics_file = self.embeddings_dir.parent / self.config['metrics_and_logging']['metrics_file']
        
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"\n✓ Metrics saved to {metrics_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve context using RAG embeddings"
    )
    parser.add_argument(
        'system_path',
        help="Path to system directory"
    )
    parser.add_argument(
        '--query',
        help="Query string for semantic search"
    )
    parser.add_argument(
        '--strategy',
        choices=['on_step_start', 'on_degradation_detected', 'on_tool_execution', 'on_user_query', 'periodic_refresh'],
        help="Retrieval strategy to use"
    )
    parser.add_argument(
        '--detect-degradation',
        help="Text to analyze for degradation signals"
    )
    parser.add_argument(
        '--format-for-injection',
        action='store_true',
        help="Format output for LLM prompt injection"
    )
    parser.add_argument(
        '--output',
        help="Output file for results (default: stdout)"
    )
    
    args = parser.parse_args()
    
    retriever = RAGContextRetriever(args.system_path)
    
    results = None
    
    if args.detect_degradation:
        signals = retriever.detect_degradation(args.detect_degradation)
        if signals:
            results = retriever.retrieve_for_degradation(signals)
    
    elif args.strategy:
        context_vars = retriever._load_current_context()
        if args.query:
            context_vars['user_query_text'] = args.query
        results = retriever.retrieve_by_strategy(args.strategy, context_vars)
    
    elif args.query:
        # Direct query mode
        context_vars = retriever._load_current_context()
        context_vars['user_query_text'] = args.query
        results = retriever.retrieve_by_strategy('on_user_query', context_vars)
    
    else:
        print("ERROR: Must specify --query, --strategy, or --detect-degradation")
        sys.exit(1)
    
    if results:
        if args.format_for_injection:
            output = retriever.format_context_for_injection(results)
        else:
            output = json.dumps(results, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"\n✓ Results saved to {args.output}")
        else:
            print("\n" + "="*80)
            print(output)
    
    retriever.save_metrics()


if __name__ == '__main__':
    main()
