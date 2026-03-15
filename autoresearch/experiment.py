#!/usr/bin/env python3
"""
Content Loop - Experiment Framework
Defines A/B tests for hooks, image styles, and CTAs to systematically improve content performance.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import random

@dataclass
class Variant:
    """A single variant in an experiment"""
    id: str
    name: str
    content: str
    category: str
    
@dataclass 
class Experiment:
    """An A/B test comparing multiple variants"""
    id: str
    name: str
    hypothesis: str
    variants: List[Variant]
    success_metric: str
    start_date: str
    duration_days: int
    status: str = "planned"

class ExperimentRunner:
    def __init__(self, config_file="config.example.yaml"):
        self.config_file = config_file
        self.data_dir = "data"
        self.log_file = os.path.join(self.data_dir, "run-log.jsonl")
        
    def create_hook_experiment(self, hook_variants: List[str], hypothesis: str) -> Experiment:
        """Create an experiment testing different hook variants"""
        variants = []
        for i, hook_text in enumerate(hook_variants):
            variant = Variant(
                id=f"hook_var_{i+1}",
                name=f"Hook Variant {chr(65+i)}",  # A, B, C...
                content=hook_text,
                category="hook"
            )
            variants.append(variant)
            
        experiment = Experiment(
            id=f"hook_test_{datetime.now().strftime('%Y%m%d_%H%M')}",
            name=f"Hook Test: {hypothesis[:50]}...",
            hypothesis=hypothesis,
            variants=variants,
            success_metric="views_per_day",
            start_date=datetime.now().isoformat(),
            duration_days=3
        )
        return experiment
    
    def create_image_experiment(self, image_styles: List[str], hypothesis: str) -> Experiment:
        """Create an experiment testing different image styles"""
        variants = []
        for i, style in enumerate(image_styles):
            variant = Variant(
                id=f"img_var_{i+1}",
                name=f"Image Style {chr(65+i)}",
                content=style,
                category="image"
            )
            variants.append(variant)
            
        experiment = Experiment(
            id=f"image_test_{datetime.now().strftime('%Y%m%d_%H%M')}",
            name=f"Image Test: {hypothesis[:50]}...",
            hypothesis=hypothesis,
            variants=variants,
            success_metric="engagement_rate",
            start_date=datetime.now().isoformat(),
            duration_days=5
        )
        return experiment
    
    def create_cta_experiment(self, cta_variants: List[str], hypothesis: str) -> Experiment:
        """Create an experiment testing different CTAs"""
        variants = []
        for i, cta_text in enumerate(cta_variants):
            variant = Variant(
                id=f"cta_var_{i+1}",
                name=f"CTA Variant {chr(65+i)}",
                content=cta_text,
                category="cta"
            )
            variants.append(variant)
            
        experiment = Experiment(
            id=f"cta_test_{datetime.now().strftime('%Y%m%d_%H%M')}",
            name=f"CTA Test: {hypothesis[:50]}...",
            hypothesis=hypothesis,
            variants=variants,
            success_metric="conversion_rate",
            start_date=datetime.now().isoformat(),
            duration_days=7
        )
        return experiment
    
    def save_experiment(self, experiment: Experiment) -> None:
        """Save experiment definition to file"""
        exp_file = os.path.join(self.data_dir, f"experiment_{experiment.id}.json")
        with open(exp_file, 'w') as f:
            # Convert dataclass to dict for JSON serialization
            exp_dict = {
                'id': experiment.id,
                'name': experiment.name,
                'hypothesis': experiment.hypothesis,
                'variants': [
                    {
                        'id': v.id,
                        'name': v.name,
                        'content': v.content,
                        'category': v.category
                    } for v in experiment.variants
                ],
                'success_metric': experiment.success_metric,
                'start_date': experiment.start_date,
                'duration_days': experiment.duration_days,
                'status': experiment.status
            }
            json.dump(exp_dict, f, indent=2)
        
        # Log experiment start
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "experiment_created",
            "experiment_id": experiment.id,
            "hypothesis": experiment.hypothesis,
            "variant_count": len(experiment.variants),
            "success_metric": experiment.success_metric
        }
        self._append_to_log(log_entry)
    
    def select_variant_for_post(self, experiment_id: str) -> Optional[Variant]:
        """Select which variant to use for next post (round-robin for fair testing)"""
        exp_file = os.path.join(self.data_dir, f"experiment_{experiment_id}.json")
        if not os.path.exists(exp_file):
            return None
            
        with open(exp_file, 'r') as f:
            exp_data = json.load(f)
        
        # Count how many times each variant has been used
        variant_usage = {}
        for variant in exp_data['variants']:
            variant_usage[variant['id']] = 0
            
        # Count usage from log
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if (entry.get('experiment_id') == experiment_id and 
                        entry.get('variant_id') in variant_usage):
                        variant_usage[entry.get('variant_id')] += 1
        
        # Select variant with minimum usage (round-robin)
        min_usage = min(variant_usage.values())
        candidates = [vid for vid, count in variant_usage.items() if count == min_usage]
        selected_variant_id = random.choice(candidates)
        
        # Find and return the variant object
        for variant_data in exp_data['variants']:
            if variant_data['id'] == selected_variant_id:
                return Variant(
                    id=variant_data['id'],
                    name=variant_data['name'],
                    content=variant_data['content'],
                    category=variant_data['category']
                )
        return None
    
    def _append_to_log(self, entry: Dict) -> None:
        """Append entry to run log"""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

def main():
    """CLI for creating and managing experiments"""
    runner = ExperimentRunner()
    
    if len(sys.argv) < 2:
        print("Usage: python experiment.py <command> [args...]")
        print("Commands:")
        print("  hook 'Hook A' 'Hook B' 'Hook C' --hypothesis 'Person conflict outperforms POV'")
        print("  image 'modern-minimal' 'cozy-warm' --hypothesis 'Minimal style gets more views'")
        print("  cta 'Download free' 'Link in bio' 'Search app store' --hypothesis 'Direct CTAs convert better'")
        print("  select experiment_id  # Select next variant for posting")
        return
    
    command = sys.argv[1]
    
    if command == "hook":
        # Extract hook variants and hypothesis
        variants = []
        hypothesis = ""
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--hypothesis" and i + 1 < len(sys.argv):
                hypothesis = sys.argv[i + 1]
                break
            variants.append(sys.argv[i])
            i += 1
            
        if len(variants) < 2:
            print("Error: Need at least 2 hook variants")
            return
            
        experiment = runner.create_hook_experiment(variants, hypothesis)
        runner.save_experiment(experiment)
        print(f"Created hook experiment: {experiment.id}")
        print(f"Variants: {[v.content for v in experiment.variants]}")
        
    elif command == "image":
        variants = []
        hypothesis = ""
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--hypothesis" and i + 1 < len(sys.argv):
                hypothesis = sys.argv[i + 1]
                break
            variants.append(sys.argv[i])
            i += 1
            
        experiment = runner.create_image_experiment(variants, hypothesis)
        runner.save_experiment(experiment)
        print(f"Created image experiment: {experiment.id}")
        
    elif command == "cta":
        variants = []
        hypothesis = ""
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--hypothesis" and i + 1 < len(sys.argv):
                hypothesis = sys.argv[i + 1]
                break
            variants.append(sys.argv[i])
            i += 1
            
        experiment = runner.create_cta_experiment(variants, hypothesis)
        runner.save_experiment(experiment)
        print(f"Created CTA experiment: {experiment.id}")
        
    elif command == "select":
        if len(sys.argv) < 3:
            print("Usage: python experiment.py select <experiment_id>")
            return
            
        experiment_id = sys.argv[2]
        variant = runner.select_variant_for_post(experiment_id)
        if variant:
            print(f"Selected variant: {variant.id} - {variant.content}")
        else:
            print(f"Experiment {experiment_id} not found")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()