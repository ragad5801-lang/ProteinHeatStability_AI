# pdb_to_fasta.py
from Bio.PDB import PDBParser, PPBuilder
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
FASTA_DIR = PROJECT_DIR / "fasta"
FASTA_DIR.mkdir(exist_ok=True)

def seq_from_pdb(pdb_path: Path) -> str:
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_path.stem, str(pdb_path))
    ppb = PPBuilder()
    peptides = ppb.build_peptides(structure)
    if not peptides:
        return ""
    # خذ أطول سلسلة
    longest = max(peptides, key=lambda p: len(p.get_sequence()))
    seq = str(longest.get_sequence()).upper()
    # استبدال حروف نادرة إلى X
    for bad in ["U", "B", "Z", "O", "J"]:
        seq = seq.replace(bad, "X")
    return seq

def main():
    pdb_files = list(PROJECT_DIR.glob("*.pdb")) + list((PROJECT_DIR / "pdbs").glob("*.pdb")) + list((PROJECT_DIR / "structures").glob("*.pdb"))
    if not pdb_files:
        print("لم أجد ملفات .pdb في المجلد. ضع ملفات PDB هنا أو داخل مجلد pdbs/ أو structures/")
        return

    for pdb in pdb_files:
        print(f"\nاستخراج التسلسل من: {pdb.name}")
        seq = seq_from_pdb(pdb)
        if not seq:
            print("⚠️ لم أستطع استخراج تسلسل من هذا الملف.")
            continue

        # اسم افتراضي = اسم الملف بدون الامتداد
        default_name = pdb.stem
        # اطلب منك اسم البروتين المطلوب (اكتب نفس الاسم اللي في CSV مثل: Wheat Protein)
        try:
            protein_id = input(f"اكتب اسم البروتين (Enter = {default_name}): ").strip()
        except EOFError:
            protein_id = default_name
        if not protein_id:
            protein_id = default_name

        # اكتب ملف FASTA
        fasta_path = FASTA_DIR / f"{protein_id}.fasta"
        with open(fasta_path, "w", encoding="utf-8") as f:
            f.write(f">{protein_id}\n")
            # نقسم السطر اختيارياً كل 60 حرف (شكل جمالي فقط)
            for i in range(0, len(seq), 60):
                f.write(seq[i:i+60] + "\n")

        print(f"✅ تم الحفظ: {fasta_path.name}")

if __name__ == "__main__":
    main()

