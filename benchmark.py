import time
import json
from typing import List, Dict, Tuple, Optional
from main import run_real_react_agent, load_config
from utils import Response
import yaml
import os
from datetime import datetime

# Test dataset with questions and expected answers
TEST_DATASET = [
    # Calculation tasks
    {"question": "What is 25 * 8?", "expected": "200", "type": "calc"},
    {"question": "Calculate (100 - 35) * 2", "expected": "130", "type": "calc"},
    {"question": "What is 2025 - 1961?", "expected": "64", "type": "calc"},
    
    # Knowledge base queries
    {"question": "When was Obama born?", "expected": "August 4, 1961", "type": "search"},
    {"question": "When was Trump born?", "expected": "June 14, 1946", "type": "search"},
    {"question": "What is the user's city?", "expected": "Chengdu", "type": "search"},
    {"question": "When was Python released?", "expected": "February 20, 1991", "type": "search"},
    
    # Multi-step reasoning
    {"question": "How much older is Trump than Obama?", "expected": "15", "type": "multi"},
    {"question": "What is Obama's age in 2025?", "expected": "64", "type": "multi"},
    {"question": "What is Trump's age in 2025?", "expected": "79", "type": "multi"},
    
    # Comparison tasks
    {"question": "Who is older, Obama or Trump?", "expected": "Trump", "type": "multi"},
    {"question": "How many years between Obama and Trump's birth?", "expected": "15", "type": "multi"},
    
    # Geography/Location
    {"question": "What cities are near Guangzhou?", "expected": ["Foshan", "Shenzhen", "Dongguan"], "type": "search"},
    {"question": "What cities are near Chengdu?", "expected": ["Leshan", "Emeishan", "Dujiangyan"], "type": "search"},
    
    # Weather queries
    {"question": "What is the weather in New York?", "expected_type": "weather_data", "type": "weather"},
    {"question": "What is the weather in London?", "expected_type": "weather_data", "type": "weather"},
    
    # Complex multi-tool tasks
    {"question": "What's the weather in Guangzhou and what cities are nearby?", "type": "complex"},
    {"question": "Calculate Obama's age and tell me the weather in his birthplace", "type": "complex"},
    
    # Mathematical expressions
    {"question": "What is (50 + 30) / 4?", "expected": "20", "type": "calc"},
    {"question": "Calculate 15 * 3 + 10", "expected": "55", "type": "calc"},
    
    # Factual queries
    {"question": "What is the hotel price per night?", "expected": "600 CNY", "type": "search"},
    {"question": "What are the recommended destinations?", "expected": ["Foshan", "Shenzhen", "Dongguan"], "type": "search"},
    
    # Edge cases
    {"question": "What is 0 * 100?", "expected": "0", "type": "calc"},
    {"question": "Calculate 100 / 4", "expected": "25", "type": "calc"},
    {"question": "What is 10 ** 2?", "expected": "100", "type": "calc"},
    
    # Multi-step with calculation
    {"question": "If Obama was born in 1961 and Trump in 1946, what's the sum of their birth years?", 
     "expected": "3907", "type": "multi"},
    {"question": "Calculate the difference between 2025 and Obama's birth year", "expected": "64", "type": "multi"},
    
    # Travel planning
    {"question": "Plan a 3-day trip from Chengdu", "expected_type": "plan", "type": "complex"},
    {"question": "What's the weather for a weekend trip to Guangzhou?", "expected_type": "weather_data", "type": "complex"},
    
    # Combined queries
    {"question": "How old will Trump be in 2030?", "expected": "84", "type": "multi"},
    {"question": "What is the total cost for 3 nights at a hotel?", "expected": "1800", "type": "calc"},
]

def check_answer_correctness(question: str, final_answer: str, expected, question_type: str) -> bool:
    """
    Check if the final answer matches the expected answer
    """
    if not final_answer:
        return False
    
    final_answer = final_answer.lower().strip()
    
    # For weather/plan types, just check if answer exists
    if question_type in ["weather", "complex"] and isinstance(expected, str) and expected == "expected_type":
        return len(final_answer) > 20  # Has substantial content
    
    if question_type in ["weather", "complex"] and isinstance(expected, dict) and "expected_type" in expected:
        return len(final_answer) > 20
    
    # For list-type expectations
    if isinstance(expected, list):
        return any(item.lower() in final_answer for item in expected)
    
    # For exact matches
    expected_str = str(expected).lower().strip()
    
    # Check if expected value is in the answer
    return expected_str in final_answer or final_answer in expected_str

def save_checkpoint(results: Dict, model_name: str, use_planner: bool, use_judgement: bool):
    """Save intermediate results to checkpoint file"""
    checkpoint_file = f"checkpoint_{model_name.replace(':', '_')}_p{int(use_planner)}_j{int(use_judgement)}.json"
    with open(checkpoint_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 Checkpoint saved to {checkpoint_file}")

def load_checkpoint(model_name: str, use_planner: bool, use_judgement: bool) -> Dict:
    """Load checkpoint if exists"""
    checkpoint_file = f"checkpoint_{model_name.replace(':', '_')}_p{int(use_planner)}_j{int(use_judgement)}.json"
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def run_benchmark(model_name: str, max_steps: int = 10, use_planner: bool = False, 
                 use_judgement: bool = False, resume: bool = True) -> Dict:
    """
    Run benchmark tests for a specific model with checkpoint support
    """
    config_name = f"Planner: {use_planner}, Judgement: {use_judgement}"
    print(f"\n{'='*60}")
    print(f"Testing Model: {model_name}")
    print(f"Configuration: {config_name}")
    print(f"{'='*60}\n")
    
    # Try to load checkpoint
    results = None
    start_idx = 0
    
    if resume:
        results = load_checkpoint(model_name, use_planner, use_judgement)
        if results:
            start_idx = len(results["test_results"])
            print(f"📂 Resuming from checkpoint: {start_idx}/{len(TEST_DATASET)} tests completed")
    
    # Initialize results if no checkpoint
    if not results:
        results = {
            "model": model_name,
            "use_planner": use_planner,
            "use_judgement": use_judgement,
            "configuration": config_name,
            "total_tests": len(TEST_DATASET),
            "successful": 0,
            "failed": 0,
            "total_steps": 0,
            "total_time": 0,
            "test_results": [],
            "started_at": datetime.now().isoformat(),
        }
    
    # Update config - DO NOT modify user_input
    cfg = load_config()
    cfg["model"]["agent_model_name"] = model_name
    cfg["agent"]["max_steps"] = max_steps
    cfg["tools"]["use_planner"] = use_planner
    cfg["tools"]["use_judgement_model"] = use_judgement
    
    # Ensure external tools are disabled
    cfg["tools"]["use_internet_search"] = False
    cfg["tools"]["use_wikipedia_search"] = False
    cfg["tools"]["use_hotel_price_lookup"] = False
    
    # Save temporary config
    with open("config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(cfg, f)
    
    for idx in range(start_idx, len(TEST_DATASET)):
        test_case = TEST_DATASET[idx]
        question = test_case["question"]
        expected = test_case.get("expected", test_case.get("expected_type"))
        q_type = test_case["type"]
        
        print(f"\n[Test {idx+1}/{len(TEST_DATASET)}] {question}")
        
        start_time = time.time()
        try:
            # Pass question directly, don't use config's user_input
            final_answer, steps_used = run_real_react_agent(
                question=question,
                max_steps=max_steps,
                use_planner=use_planner,
                use_judgement_model=use_judgement
            )
            elapsed_time = time.time() - start_time
            
            is_correct = check_answer_correctness(question, final_answer, expected, q_type)
            
            result = {
                "question": question,
                "expected": expected,
                "final_answer": final_answer,
                "steps": steps_used,
                "time": round(elapsed_time, 2),
                "correct": is_correct,
                "type": q_type,
                "timestamp": datetime.now().isoformat()
            }
            
            results["test_results"].append(result)
            results["total_steps"] += steps_used
            results["total_time"] += elapsed_time
            
            if is_correct:
                results["successful"] += 1
                print(f"✅ PASS (Steps: {steps_used}, Time: {elapsed_time:.2f}s)")
            else:
                results["failed"] += 1
                print(f"❌ FAIL (Steps: {steps_used}, Time: {elapsed_time:.2f}s)")
                print(f"   Expected: {expected}")
                print(f"   Got: {final_answer}")
        
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ ERROR: {str(e)}")
            results["failed"] += 1
            results["test_results"].append({
                "question": question,
                "expected": expected,
                "error": str(e),
                "time": round(elapsed_time, 2),
                "correct": False,
                "type": q_type,
                "timestamp": datetime.now().isoformat()
            })
        
        # Save checkpoint after each test
        save_checkpoint(results, model_name, use_planner, use_judgement)
    
    # Calculate metrics
    results["success_rate"] = (results["successful"] / results["total_tests"]) * 100
    results["avg_steps"] = results["total_steps"] / results["total_tests"] if results["total_tests"] > 0 else 0
    results["avg_time"] = results["total_time"] / results["total_tests"] if results["total_tests"] > 0 else 0
    results["completed_at"] = datetime.now().isoformat()
    
    # Save final results
    final_file = f"benchmark_{model_name.replace(':', '_')}_p{int(use_planner)}_j{int(use_judgement)}.json"
    with open(final_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Clean up checkpoint
    checkpoint_file = f"checkpoint_{model_name.replace(':', '_')}_p{int(use_planner)}_j{int(use_judgement)}.json"
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
        print(f"🗑️  Checkpoint cleaned up")
    
    return results

def get_next_config_to_test(model: str, all_configs: List[Dict]) -> Optional[Dict]:
    """
    Check which configurations have been completed and return the next one to test
    """
    for config in all_configs:
        result_file = f"benchmark_{model.replace(':', '_')}_p{int(config['planner'])}_j{int(config['judgement'])}.json"
        
        # Check if this config has a completed result file
        if os.path.exists(result_file):
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # If completed and has all tests, skip
                if "completed_at" in data and len(data["test_results"]) == len(TEST_DATASET):
                    print(f"✓ {config['name']} already completed, skipping...")
                    continue
        
        # This config needs to be tested
        return config
    
    return None

def run_all_configurations(model: str, resume: bool = True, start_from_config: Optional[str] = None):
    """
    Test all 4 configurations for a single model:
    1. Base (no planner, no judgement)
    2. Base + Judgement
    3. Base + Planner
    4. Base + Planner + Judgement
    
    Args:
        start_from_config: Skip to specific config ("p0_j0", "p0_j1", "p1_j0", "p1_j1")
    """
    configurations = [
        {"planner": False, "judgement": False, "name": "Base Model", "code": "p0_j0"},
        {"planner": False, "judgement": True, "name": "Base + Judgement", "code": "p0_j1"},
        {"planner": True, "judgement": False, "name": "Base + Planner", "code": "p1_j0"},
        {"planner": True, "judgement": True, "name": "Base + Planner + Judgement", "code": "p1_j1"},
    ]
    
    # If start_from_config specified, skip earlier configs
    if start_from_config:
        start_idx = next((i for i, c in enumerate(configurations) if c['code'] == start_from_config), 0)
        configurations = configurations[start_idx:]
        print(f"🔄 Restarting from configuration: {configurations[0]['name']}")
    
    all_results = []
    
    for config in configurations:
        print(f"\n{'#'*80}")
        print(f"# Configuration: {config['name']} ({config['code']})")
        print(f"{'#'*80}")
        
        # Check if already completed
        result_file = f"benchmark_{model.replace(':', '_')}_{config['code']}.json"
        if os.path.exists(result_file) and not resume:
            with open(result_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                if "completed_at" in existing_data and len(existing_data["test_results"]) == len(TEST_DATASET):
                    print(f"✓ Already completed with {len(existing_data['test_results'])} tests, loading results...")
                    all_results.append(existing_data)
                    continue
        
        try:
            results = run_benchmark(
                model_name=model,
                use_planner=config["planner"],
                use_judgement=config["judgement"],
                resume=resume
            )
            all_results.append(results)
        except KeyboardInterrupt:
            print(f"\n⚠️  Interrupted at {config['name']}!")
            print(f"To resume, run: restart_from('{model}', '{config['code']}')")
            return all_results
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
            continue
    
    return all_results

def restart_from(model: str, config_code: str):
    """
    Convenience function to restart from a specific configuration
    
    Usage:
        restart_from("llama3.1:8b", "p1_j0")
    """
    print(f"🔄 Restarting {model} from configuration {config_code}")
    results = run_all_configurations(model, resume=True, start_from_config=config_code)
    
    # Generate comparison with existing results
    all_results = load_all_existing_results(model)
    all_results.extend(results)
    
    print_comparison_table([model], all_results)
    save_comparison(all_results)

def load_all_existing_results(model: str) -> List[Dict]:
    """
    Load all existing benchmark results for a model
    """
    configs = ["p0_j0", "p0_j1", "p1_j0", "p1_j1"]
    all_results = []
    
    for config in configs:
        result_file = f"benchmark_{model.replace(':', '_')}_{config}.json"
        if os.path.exists(result_file):
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "completed_at" in data:
                    all_results.append(data)
                    print(f"✓ Loaded existing result: {config}")
    
    return all_results

def print_comparison_table(models: List[str], all_results: List[Dict]):
    """
    Print formatted comparison table
    """
    print(f"\n{'='*100}")
    print("COMPREHENSIVE BENCHMARK COMPARISON")
    print(f"{'='*100}\n")
    print(f"{'Model':<15} {'Configuration':<30} {'Success Rate':<15} {'Avg Steps':<12} {'Avg Time (s)':<15}")
    print(f"{'-'*100}")
    
    for result in all_results:
        config_str = f"P:{int(result['use_planner'])} J:{int(result['use_judgement'])}"
        print(f"{result['model']:<15} "
              f"{config_str:<30} "
              f"{result['success_rate']:.1f}%{'':<10} "
              f"{result['avg_steps']:.2f}{'':<8} "
              f"{result['avg_time']:.2f}")

def save_comparison(all_results: List[Dict]):
    """
    Save comparison to file
    """
    comparison_file = f"benchmark_comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(comparison_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Comprehensive comparison saved to {comparison_file}")

def compare_all_results(models: List[str], resume: bool = True):
    """
    Run all configurations for all models and generate comparison
    """
    all_results = []
    
    for model in models:
        print(f"\n{'='*80}")
        print(f"TESTING MODEL: {model}")
        print(f"{'='*80}")
        
        model_results = run_all_configurations(model, resume=resume)
        all_results.extend(model_results)
    
    print_comparison_table(models, all_results)
    save_comparison(all_results)
    
    return all_results

def main():
    # Models to test
    models_to_test = [
        "llama3.1:8b",
        "gemma3:4b", 
        "qwen3:8b"
    ]
    
    print("="*80)
    print("COMPREHENSIVE BENCHMARK TEST")
    print("="*80)
    print(f"\nModels: {', '.join(models_to_test)}")
    print(f"Total test cases: {len(TEST_DATASET)}")
    print("\nConfigurations to test:")
    print("  1. Base Model (p0_j0)")
    print("  2. Base + Judgement Model (p0_j1)")
    print("  3. Base + Planner (p1_j0)")
    print("  4. Base + Planner + Judgement Model (p1_j1)")
    print("\n💡 Tests auto-save after each question. Safe to interrupt and resume.")
    print("⚠️  External tools (internet search, wikipedia, hotel lookup) are DISABLED")
    print("\n🔄 To restart from a specific config: restart_from('model_name', 'p1_j0')")
    print("="*80)
    
    try:
        results = compare_all_results(models_to_test, resume=True)
        print("\n✅ All benchmarks completed! Results saved to JSON files.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user. Progress has been saved.")
        print("Run the script again to resume from where you left off.")

# Convenience function for manual restart
def manual_restart():
    """
    Interactive function to restart from a specific point
    """
    print("\nAvailable models:")
    models = ["llama3.1:8b", "gemma3:4b", "qwen3:8b"]
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model}")
    
    model_choice = int(input("\nSelect model (1-3): ")) - 1
    model = models[model_choice]
    
    print("\nAvailable configurations:")
    configs = [
        ("p0_j0", "Base Model"),
        ("p0_j1", "Base + Judgement"),
        ("p1_j0", "Base + Planner"),
        ("p1_j1", "Base + Planner + Judgement")
    ]
    for i, (code, name) in enumerate(configs, 1):
        print(f"  {i}. {code} - {name}")
    
    config_choice = int(input("\nSelect configuration (1-4): ")) - 1
    config_code = configs[config_choice][0]
    
    restart_from(model, config_code)

if __name__ == "__main__":
    import sys
    
    # Check if manual restart requested
    if len(sys.argv) > 1 and sys.argv[1] == "restart":
        if len(sys.argv) >= 4:
            # python benchmark.py restart llama3.1:8b p1_j0
            restart_from(sys.argv[2], sys.argv[3])
        else:
            manual_restart()
    else:
        main()