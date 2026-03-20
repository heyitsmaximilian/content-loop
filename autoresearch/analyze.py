#!/usr/bin/env python3
"""
Content Loop - Performance Analysis
Pulls post analytics, computes variant performance, identifies winners/losers.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import statistics

from config import Config

@dataclass
class PostMetrics:
    """Metrics for a single post"""
    post_id: str
    timestamp: str
    hook_category: str
    hook_text: str
    variant_id: Optional[str]
    experiment_id: Optional[str]
    views: int
    likes: int
    comments: int
    shares: int
    product: str = ""
    conversions: int = 0

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate (likes + comments + shares) / views"""
        if self.views == 0:
            return 0.0
        return (self.likes + self.comments + self.shares) / self.views
    
    @property 
    def conversion_rate(self) -> float:
        """Calculate conversion rate"""
        if self.views == 0:
            return 0.0
        return self.conversions / self.views

@dataclass
class VariantPerformance:
    """Performance summary for a variant"""
    variant_id: str
    variant_name: str
    content: str
    category: str
    post_count: int
    total_views: int
    total_conversions: int
    avg_views: float
    avg_engagement_rate: float
    avg_conversion_rate: float
    performance_score: float

class AnalysisEngine:
    def __init__(self, data_dir="data", config: Config = None):
        self.config = config or Config()
        self.data_dir = self.config.data_dir if config else data_dir
        self.log_file = self.config.log_file if config else os.path.join(data_dir, "run-log.jsonl")
        self.product = self.config.product
    
    def load_post_metrics(self, days_back: int = 7) -> List[PostMetrics]:
        """Load post metrics from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        posts = []
        
        if not os.path.exists(self.log_file):
            return posts
            
        with open(self.log_file, 'r') as f:
            for line in f:
                entry = json.loads(line.strip())
                if entry.get('type') != 'post':
                    continue

                # Filter by product if set
                if self.product and self.product != "default":
                    if entry.get('product', '') != self.product:
                        continue
                    
                post_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                if post_date < cutoff_date:
                    continue
                
                post = PostMetrics(
                    post_id=entry.get('post_id', 'unknown'),
                    timestamp=entry['timestamp'],
                    hook_category=entry.get('hook', entry.get('hook_category', 'unknown')),
                    hook_text=entry.get('hook_text', ''),
                    variant_id=entry.get('variant_id'),
                    experiment_id=entry.get('experiment_id'),
                    views=entry.get('views', 0),
                    likes=entry.get('likes', 0),
                    comments=entry.get('comments', 0),
                    shares=entry.get('shares', 0),
                    product=entry.get('product', ''),
                    conversions=entry.get('conversion', entry.get('conversions', 0))
                )
                posts.append(post)
        
        return sorted(posts, key=lambda p: p.timestamp, reverse=True)
    
    def analyze_hook_performance(self, posts: List[PostMetrics]) -> Dict[str, VariantPerformance]:
        """Analyze performance by hook category"""
        hook_stats = defaultdict(list)
        
        for post in posts:
            hook_stats[post.hook_category].append(post)
        
        performances = {}
        for hook_category, hook_posts in hook_stats.items():
            if not hook_posts:
                continue
                
            total_views = sum(p.views for p in hook_posts)
            total_conversions = sum(p.conversions for p in hook_posts)
            avg_views = statistics.mean(p.views for p in hook_posts)
            avg_engagement = statistics.mean(p.engagement_rate for p in hook_posts)
            avg_conversion = statistics.mean(p.conversion_rate for p in hook_posts)
            
            # Performance score: weighted combination of views and conversions
            # Higher weight on conversions if we have conversion data
            has_conversions = any(p.conversions > 0 for p in hook_posts)
            if has_conversions:
                performance_score = (avg_views / 1000) * 0.3 + (avg_conversion * 100) * 0.7
            else:
                performance_score = (avg_views / 1000) * 0.7 + (avg_engagement * 100) * 0.3
            
            performance = VariantPerformance(
                variant_id=hook_category,
                variant_name=hook_category.replace('-', ' ').title(),
                content=hook_posts[0].hook_text or hook_category,
                category="hook",
                post_count=len(hook_posts),
                total_views=total_views,
                total_conversions=total_conversions,
                avg_views=avg_views,
                avg_engagement_rate=avg_engagement,
                avg_conversion_rate=avg_conversion,
                performance_score=performance_score
            )
            performances[hook_category] = performance
        
        return performances
    
    def analyze_experiment_performance(self, experiment_id: str, posts: List[PostMetrics]) -> Dict[str, VariantPerformance]:
        """Analyze performance for a specific experiment"""
        experiment_posts = [p for p in posts if p.experiment_id == experiment_id]
        if not experiment_posts:
            return {}
        
        variant_stats = defaultdict(list)
        for post in experiment_posts:
            if post.variant_id:
                variant_stats[post.variant_id].append(post)
        
        performances = {}
        for variant_id, variant_posts in variant_stats.items():
            if not variant_posts:
                continue
                
            total_views = sum(p.views for p in variant_posts)
            total_conversions = sum(p.conversions for p in variant_posts)
            avg_views = statistics.mean(p.views for p in variant_posts)
            avg_engagement = statistics.mean(p.engagement_rate for p in variant_posts)
            avg_conversion = statistics.mean(p.conversion_rate for p in variant_posts)
            
            # Load experiment details to get variant content
            exp_file = os.path.join(self.data_dir, f"experiment_{experiment_id}.json")
            variant_content = variant_id
            variant_name = variant_id
            category = "unknown"
            
            if os.path.exists(exp_file):
                with open(exp_file, 'r') as f:
                    exp_data = json.load(f)
                    for v in exp_data.get('variants', []):
                        if v['id'] == variant_id:
                            variant_content = v['content']
                            variant_name = v['name']
                            category = v['category']
                            break
            
            has_conversions = any(p.conversions > 0 for p in variant_posts)
            if has_conversions:
                performance_score = (avg_views / 1000) * 0.3 + (avg_conversion * 100) * 0.7
            else:
                performance_score = (avg_views / 1000) * 0.7 + (avg_engagement * 100) * 0.3
            
            performance = VariantPerformance(
                variant_id=variant_id,
                variant_name=variant_name,
                content=variant_content,
                category=category,
                post_count=len(variant_posts),
                total_views=total_views,
                total_conversions=total_conversions,
                avg_views=avg_views,
                avg_engagement_rate=avg_engagement,
                avg_conversion_rate=avg_conversion,
                performance_score=performance_score
            )
            performances[variant_id] = performance
        
        return performances
    
    def identify_winners_losers(self, performances: Dict[str, VariantPerformance]) -> Tuple[List[VariantPerformance], List[VariantPerformance]]:
        """Identify winning and losing variants based on performance"""
        if len(performances) < 2:
            return list(performances.values()), []
        
        sorted_variants = sorted(performances.values(), key=lambda v: v.performance_score, reverse=True)
        
        # Top 30% are winners, bottom 30% are losers
        winner_count = max(1, len(sorted_variants) // 3)
        loser_count = max(1, len(sorted_variants) // 3)
        
        winners = sorted_variants[:winner_count]
        losers = sorted_variants[-loser_count:]
        
        # Additional criteria: variants with >30% performance degradation are losers
        if len(sorted_variants) > 1:
            best_score = sorted_variants[0].performance_score
            degradation_threshold = best_score * 0.7  # 30% degradation
            
            additional_losers = [v for v in sorted_variants if v.performance_score < degradation_threshold and v not in losers]
            losers.extend(additional_losers)
        
        return winners, losers
    
    def generate_report(self, days_back: int = 3) -> Dict:
        """Generate comprehensive analysis report"""
        posts = self.load_post_metrics(days_back)
        
        if not posts:
            return {
                "timestamp": datetime.now().isoformat(),
                "period": f"Last {days_back} days",
                "total_posts": 0,
                "message": "No post data found for analysis",
                "recommendations": ["Create some posts and try again"]
            }
        
        # Overall performance
        total_views = sum(p.views for p in posts)
        total_conversions = sum(p.conversions for p in posts)
        avg_views = total_views / len(posts) if posts else 0
        overall_conversion_rate = total_conversions / total_views if total_views > 0 else 0
        
        # Hook performance analysis
        hook_performances = self.analyze_hook_performance(posts)
        hook_winners, hook_losers = self.identify_winners_losers(hook_performances)
        
        # Find active experiments
        active_experiments = set(p.experiment_id for p in posts if p.experiment_id)
        experiment_results = {}
        
        for exp_id in active_experiments:
            exp_performances = self.analyze_experiment_performance(exp_id, posts)
            if exp_performances:
                exp_winners, exp_losers = self.identify_winners_losers(exp_performances)
                experiment_results[exp_id] = {
                    "variants": exp_performances,
                    "winners": exp_winners,
                    "losers": exp_losers
                }
        
        # Generate findings and recommendations
        findings = []
        recommendations = []
        
        if hook_winners:
            best_hook = hook_winners[0]
            findings.append(f"{best_hook.variant_name} hooks are top performers with {best_hook.avg_views:.0f} avg views")
            recommendations.append(f"Double down on {best_hook.variant_name} hooks - create 3 variations")
        
        if hook_losers:
            worst_hook = hook_losers[0]
            findings.append(f"{worst_hook.variant_name} hooks underperforming with only {worst_hook.avg_views:.0f} avg views")
            recommendations.append(f"Drop {worst_hook.variant_name} hooks - try different formats")
        
        # Conversion analysis
        has_conversion_data = any(p.conversions > 0 for p in posts)
        if has_conversion_data:
            high_view_posts = [p for p in posts if p.views > avg_views]
            high_conversion_posts = [p for p in posts if p.conversions > 0]
            
            if high_view_posts and not high_conversion_posts:
                findings.append("High views but low conversions - hook works, CTA needs fixing")
                recommendations.append("Test different CTAs: 'download free', 'link in bio', 'search app store'")
            elif high_conversion_posts and not high_view_posts:
                findings.append("Good conversions but low views - content works, hook needs improvement")
                recommendations.append("Test stronger hooks: person+conflict, challenge format, before/after reveals")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "product": self.product,
            "period": f"Last {days_back} days",
            "total_posts": len(posts),
            "total_views": total_views,
            "total_conversions": total_conversions,
            "avg_views_per_post": avg_views,
            "overall_conversion_rate": overall_conversion_rate,
            "hook_performances": {k: {
                "avg_views": v.avg_views,
                "avg_engagement_rate": v.avg_engagement_rate,
                "avg_conversion_rate": v.avg_conversion_rate,
                "performance_score": v.performance_score,
                "post_count": v.post_count
            } for k, v in hook_performances.items()},
            "winners": [v.variant_name for v in hook_winners],
            "losers": [v.variant_name for v in hook_losers],
            "experiment_results": experiment_results,
            "findings": findings,
            "recommendations": recommendations
        }

def main():
    """CLI for running analysis"""
    cfg = Config()
    engine = AnalysisEngine(config=cfg)
    print(f"[product: {cfg.product}]")
    
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <command> [args...]")
        print("Commands:")
        print("  report [days]     # Generate performance report for last N days (default: 3)")
        print("  hooks [days]      # Analyze hook performance")
        print("  experiment <id>   # Analyze specific experiment")
        return
    
    command = sys.argv[1]
    
    if command == "report":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        report = engine.generate_report(days)
        
        print(f"\n=== CONTENT PERFORMANCE REPORT ===")
        print(f"Period: {report['period']}")
        print(f"Total posts: {report['total_posts']}")
        print(f"Total views: {report['total_views']:,}")
        print(f"Average views per post: {report['avg_views_per_post']:.0f}")
        
        if report['total_conversions'] > 0:
            print(f"Total conversions: {report['total_conversions']}")
            print(f"Overall conversion rate: {report['overall_conversion_rate']:.3%}")
        
        if report['winners']:
            print(f"\n🏆 WINNERS: {', '.join(report['winners'])}")
        
        if report['losers']:
            print(f"❌ LOSERS: {', '.join(report['losers'])}")
        
        if report['findings']:
            print("\n📊 FINDINGS:")
            for finding in report['findings']:
                print(f"  • {finding}")
        
        if report['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        # Save report
        report_file = os.path.join(engine.data_dir, f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved: {report_file}")
        
    elif command == "hooks":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        posts = engine.load_post_metrics(days)
        performances = engine.analyze_hook_performance(posts)
        
        print(f"\n=== HOOK PERFORMANCE ({days} days) ===")
        for hook_id, perf in sorted(performances.items(), key=lambda x: x[1].performance_score, reverse=True):
            print(f"{hook_id:20} | {perf.avg_views:6.0f} views | {perf.avg_engagement_rate:5.1%} eng | Score: {perf.performance_score:.1f}")
        
    elif command == "experiment":
        if len(sys.argv) < 3:
            print("Usage: python analyze.py experiment <experiment_id>")
            return
            
        exp_id = sys.argv[2]
        posts = engine.load_post_metrics(30)  # Look back further for experiments
        performances = engine.analyze_experiment_performance(exp_id, posts)
        
        if not performances:
            print(f"No data found for experiment: {exp_id}")
            return
            
        print(f"\n=== EXPERIMENT RESULTS: {exp_id} ===")
        for variant_id, perf in sorted(performances.items(), key=lambda x: x[1].performance_score, reverse=True):
            print(f"{variant_id:15} | {perf.avg_views:6.0f} views | {perf.avg_conversion_rate:5.1%} conv | Score: {perf.performance_score:.1f}")
            print(f"{'':15} | Content: {perf.content[:60]}...")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()