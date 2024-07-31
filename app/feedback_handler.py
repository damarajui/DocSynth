import logging

from app.database import get_guide_by_id, store_feedback_data, update_guide_rating
from app.models import FeedbackData, SetupGuide
from app.summarizer import regenerate_setup_guide

logger = logging.getLogger(__name__)

async def handle_feedback(feedback: FeedbackData):
    try:
        await update_guide_rating(feedback.guide_id, feedback.rating)
        logger.info(f"Updated rating for guide {feedback.guide_id}: {feedback.rating}")
        
        if feedback.rating < 3:
            new_guide = await trigger_guide_review(feedback)
            if new_guide:
                return new_guide
        
        await store_feedback_data(feedback)
        logger.info(f"Stored feedback for guide {feedback.guide_id}")
        
        return None
    except Exception as e:
        logger.error(f"Error handling feedback for guide {feedback.guide_id}: {str(e)}")
        raise

async def trigger_guide_review(feedback: FeedbackData) -> SetupGuide | None:
    try:
        guide = await get_guide_by_id(feedback.guide_id)
        if guide:
            new_guide = await regenerate_setup_guide(guide, feedback.comments)
            logger.info(f"Regenerated guide {feedback.guide_id} based on feedback")
            return new_guide
        else:
            logger.warning(f"Guide {feedback.guide_id} not found for review")
            return None
    except Exception as e:
        logger.error(f"Error reviewing guide {feedback.guide_id}: {str(e)}")
        return None

def analyze_feedback_trends():
    # Implement analysis of feedback trends
    # This could be used to improve the guide generation process over time
    pass