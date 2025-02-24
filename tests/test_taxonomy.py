"""Test taxonomy validation."""
import pytest
from src.tagging.taxonomy.structure import (
    TaxonomyStructure,
    TaxonomyValidationError,
    InvalidCategoryError,
    InvalidTagError,
    MissingRequiredFieldError,
    InvalidFormatError
)

@pytest.fixture
def taxonomy():
    """Create a taxonomy instance for testing."""
    return TaxonomyStructure()

@pytest.fixture
def valid_tags():
    """Create a valid set of tags for testing."""
    return {
        "Format": ["Series Episodes"],
        "Theme": ["Ancient & Classical Civilizations"],
        "Track": ["Roman Track"],
        "episode_number": 1
    }

def test_taxonomy_structure_isomorphic():
    """Test that TaxonomyStructure.to_dict() matches the original taxonomy dictionary."""
    original_taxonomy = {
        "Format": [
            "Series Episodes",
            "Standalone Episodes",
            "RIHC Series"
        ],
        "Theme": [
            "Ancient & Classical Civilizations",
            "Medieval & Renaissance Europe",
            "Empire, Colonialism & Exploration",
            "Modern History",
            "Military History & Battles",
            "Social & Cultural History",
            "Economic History",
            "Political History",
            "Religious History",
            "Scientific & Technological History"
        ],
        "Track": [
            "Roman Track",
            "Medieval & Renaissance Track",
            "Modern Track",
            "Military & Battles Track",
            "Social Track",
            "Economic Track",
            "Political Track",
            "Religious Track",
            "Scientific Track",
            "The RIHC Bonus Track"
        ]
    }
    
    taxonomy_structure = TaxonomyStructure()
    converted_dict = taxonomy_structure.to_dict()
    
    # Test structure is identical
    assert set(original_taxonomy.keys()) == set(converted_dict.keys())
    
    # Test each category has identical tags (order independent)
    for category in original_taxonomy:
        assert set(original_taxonomy[category]) == set(converted_dict[category])
        
    # Test each category maintains original order
    for category in original_taxonomy:
        assert original_taxonomy[category] == converted_dict[category]

def test_validate_invalid_category(taxonomy):
    """Test that unknown category fails validation."""
    tags = {"InvalidCategory": ["Series Episodes"]}
    with pytest.raises(MissingRequiredFieldError):
        taxonomy.validate_tags(tags)

def test_validate_invalid_tag_in_format(taxonomy, valid_tags):
    """Test that invalid Format tag fails."""
    tags = valid_tags.copy()
    tags["Format"] = ["InvalidTag"]
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags)

def test_validate_invalid_tag_in_theme(taxonomy, valid_tags):
    """Test that invalid Theme tag fails."""
    tags = valid_tags.copy()
    tags["Theme"] = ["InvalidTag"]
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags)

def test_validate_invalid_tag_in_track(taxonomy, valid_tags):
    """Test that invalid Track tag fails."""
    tags = valid_tags.copy()
    tags["Track"] = ["InvalidTag"]
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags)

def test_validate_missing_format(taxonomy, valid_tags):
    """Test missing Format field fails."""
    tags = valid_tags.copy()
    del tags["Format"]
    with pytest.raises(MissingRequiredFieldError):
        taxonomy.validate_tags(tags)

def test_validate_missing_theme(taxonomy, valid_tags):
    """Test missing Theme field fails."""
    tags = valid_tags.copy()
    del tags["Theme"]
    with pytest.raises(MissingRequiredFieldError):
        taxonomy.validate_tags(tags)

def test_validate_missing_track(taxonomy, valid_tags):
    """Test missing Track field fails."""
    tags = valid_tags.copy()
    del tags["Track"]
    with pytest.raises(MissingRequiredFieldError):
        taxonomy.validate_tags(tags)

def test_validate_missing_episode_number(taxonomy, valid_tags):
    """Test missing episode_number field fails."""
    tags = valid_tags.copy()
    del tags["episode_number"]
    with pytest.raises(MissingRequiredFieldError):
        taxonomy.validate_tags(tags)

def test_validate_non_list_format(taxonomy, valid_tags):
    """Test non-list Format fails."""
    tags = valid_tags.copy()
    tags["Format"] = "Series Episodes"
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags)

def test_validate_non_list_theme(taxonomy, valid_tags):
    """Test non-list Theme fails."""
    tags = valid_tags.copy()
    tags["Theme"] = "Ancient & Classical Civilizations"
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags)

def test_validate_non_list_track(taxonomy, valid_tags):
    """Test non-list Track fails."""
    tags = valid_tags.copy()
    tags["Track"] = "Roman Track"
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags)

def test_validate_multiple_format_tags(taxonomy, valid_tags):
    """Test multiple Format tags fail."""
    tags = valid_tags.copy()
    tags["Format"] = ["Series Episodes", "Standalone Episodes"]
    with pytest.raises(InvalidFormatError):
        taxonomy.validate_tags(tags)

def test_validate_rihc_without_series(taxonomy, valid_tags):
    """Test RIHC Series without Series Episodes fails."""
    tags = valid_tags.copy()
    tags["Format"] = ["RIHC Series"]
    with pytest.raises(InvalidFormatError):
        taxonomy.validate_tags(tags)

def test_validate_invalid_episode_number_type(taxonomy, valid_tags):
    """Test invalid episode_number type fails."""
    tags = valid_tags.copy()
    tags["episode_number"] = "1"  # String instead of int
    with pytest.raises(InvalidTagError):
        taxonomy.validate_tags(tags)

def test_validate_valid_tags(taxonomy, valid_tags):
    """Test that valid tags pass."""
    # Test with episode number
    taxonomy.validate_tags(valid_tags)
    
    # Test with null episode number
    tags = valid_tags.copy()
    tags["episode_number"] = None
    taxonomy.validate_tags(tags)
    
    # Test with RIHC Series + Series Episodes
    tags = valid_tags.copy()
    tags["Format"] = ["RIHC Series", "Series Episodes"]
    taxonomy.validate_tags(tags)
    
    # Test with multiple themes and tracks
    tags = valid_tags.copy()
    tags["Theme"] = [
        "Ancient & Classical Civilizations",
        "Military History & Battles"
    ]
    tags["Track"] = [
        "Roman Track",
        "Military & Battles Track"
    ]
    taxonomy.validate_tags(tags) 