import cyvcf2
from rag_agent import analyze_variant

def process_vcf(vcf_path):
    print(f"📂 Reading VCF file: {vcf_path}")
    vcf = cyvcf2.VCF(vcf_path)
    
    # Loop through variants
    for variant in vcf:
        # Filter: Only look at High Quality variants (QUAL > 50)
        if variant.QUAL and variant.QUAL > 50:
            
            # 1. Convert VCF record to Natural Language
            # Example: "Gene EGFR, Mutation C>T at pos 552424"
            variant_text = f"Variant on Chromosome {variant.CHROM} at position {variant.POS}. Ref: {variant.REF}, Alt: {variant.ALT[0]}."
            
            # Check if we can identify the gene (Basic logic, usually requires annotation tool like snpEff)
            # For this demo, we assume the user provides a VCF that is already annotated or we focus on known loci.
            print(f"\n🔍 Analyzing: {variant_text}")
            
            # 2. Ask the AI Agent
            report = analyze_variant(variant_text)
            
            print(f"🤖 AI Report:\n{report}")
            print("-" * 50)

if __name__ == "__main__":
    vcf_path = "/Users/archanasingh/Documents/Parmarth/clingen-ai/15586_all_merge_output_ainfo.vcf"
    process_vcf(vcf_path)