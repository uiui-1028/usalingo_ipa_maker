# Output Directory

This directory contains the final output files from the IPA processing pipeline.

## Files

- `final_corrected_words_with_ipa.csv` - Final IPA dataset with standardized IPA notation
  - Contains 7,321 words with IPA transcriptions
  - 99.8% from CMU dictionary, 0.2% generated
  - 100% coverage with standardized IPA format
  
- `corrected_cmu_dict.csv` - Corrected CMU dictionary (reference)
  - Contains the original CMU dictionary with IPA corrections
  - Used as reference for the main dataset

## Data Format

The main dataset (`final_corrected_words_with_ipa.csv`) contains:
- `word`: The English word
- `ipa`: IPA transcription in standardized format
- `source`: Data source (cmu_dict or generated)

## IPA Standardization

The IPA data has been standardized according to:
- /ɝ/ → /ɜːr/ conversion for American English
- /ɹ/ → /r/ unification
- Proper stress marking with ˈ and ˌ
- Consistent long vowel notation with ː
