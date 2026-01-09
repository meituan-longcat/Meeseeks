import re
from ..utils import clean_up_text

def model_each_length(range, model_response):
    """Check if each response item's character length is within specified range"""
    res_len = -1
    for item in model_response:
        cleaned_text = clean_up_text(item)
        res_len = len(cleaned_text)

        if not range[0] <= res_len <= range[1]:
            return 0, f"❌ Content character count does not match range {range}: [{str(cleaned_text)}] count is: {str(res_len)}"
    return 1, f"✅ All content character counts match"


def model_total_length(range, model_response):
    """Check if total character length of all response items is within specified range"""
    total_len = 0
    for item in model_response:
        cleaned_text = clean_up_text(item)
        res_len = len(cleaned_text)
        total_len += res_len
    if not range[0] <= total_len <= range[1]:
        return 0, f"❌ Cleaned character count does not match range {range}: model_response total count is: {str(total_len)}"
    return 1, f"✅ Cleaned character count matches, model_response total count is {str(total_len)}"

def model_item_count(range, model_response):
    """Check if number of response items is within specified range"""
    res_len = len(model_response)
    if not range[0] <= res_len <= range[1]:
        return 0, f"❌ Count mismatch, generated item count is: {str(res_len)}"
    return 1, f"✅ Count matches, generated item count is {str(res_len)}"

def model_repeat_each(model_response):
    """Check if there are duplicate elements in response items"""
    cleaned_responses = [clean_up_text(item) for item in model_response]

    # Create dictionary to record occurrence count of each element
    item_count = {}
    for item in cleaned_responses:
        if item in item_count:
            item_count[item] += 1
        else:
            item_count[item] = 1

    # Find duplicates
    duplicates = [item for item, count in item_count.items() if count > 1]

    if duplicates:
        duplicate_info = ", ".join([f"'{item}' (appears {item_count[item]} times)" for item in duplicates])
        return 0, f"❌ Duplicates found: {duplicate_info}"

    return 1, "✅ No duplicates"


def model_no_word_repeat(model_response):
    """Check if there are duplicate characters across all response items"""
    model_response = [clean_up_text(i) for i in model_response]

    all_characters = []
    duplicates = []

    for item in model_response:
        for character in item:
            if character not in all_characters:
                all_characters.append(character)
            elif character not in duplicates:
                # If character is already in all_characters but not in duplicates,
                # add it to duplicates list
                duplicates.append(character)

    if duplicates:
        # Format duplicate character output, clearly indicating which characters are duplicated
        if len(duplicates) <= 10:
            duplicate_list = ", ".join([f"'{char}'" for char in duplicates])
            duplicate_info = f"Characters {duplicate_list} are duplicated"
        else:
            duplicate_list = ", ".join([f"'{char}'" for char in duplicates[:10]])
            duplicate_info = f"Characters {duplicate_list} and {len(duplicates)} other characters are duplicated"

        return 0, f"❌ Duplicates detected: {duplicate_info}"

    return 1, "✅ No duplicates"



def model_non_very_similar(sentences_list):
    """Check similarity between sentences, if two sentences have character overlap rate > 75%, consider as mismatch"""
    for i in range(len(sentences_list)):
        sentences_list[i] = clean_up_text(sentences_list[i])

    def calculate_similarity(sentence1, sentence2):
        # Convert sentences to character sets
        chars1 = set(sentence1)
        chars2 = set(sentence2)

        # Calculate common character count
        common_chars = chars1.intersection(chars2)

        # Calculate overlap rate
        total_chars = len(chars1) + len(chars2)
        if total_chars == 0:
            return 0
        similarity_rate = (2 * len(common_chars)) / total_chars
        return similarity_rate

    # Iterate through all sentence pairs
    for i in range(len(sentences_list)):
        for j in range(i + 1, len(sentences_list)):
            sentence1 = sentences_list[i]
            sentence2 = sentences_list[j]
            similarity_rate = calculate_similarity(sentence1, sentence2)

            # Check if overlap rate exceeds 75%
            if similarity_rate > 0.75:
                return 0, f"❌ Sentence pair mismatch due to high similarity: \n1: {sentence1}\n2: {sentence2}\nSimilarity: {similarity_rate:.2f}"
    return 1, "✅ No particularly similar sentences"
