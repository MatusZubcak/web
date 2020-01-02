from django import template
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ungettext as _

register = template.Library()


@register.inclusion_tag("trojsten/polls/parts/progress.html", takes_context=True)
def show_time(context, current_question):
    start = current_question.created_date
    end = current_question.deadline
    full = end - start
    remaining = end - timezone.now()
    elapsed = full - remaining
    if remaining.days <= settings.ROUND_PROGRESS_DANGER_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_DANGER_CLASS
    elif remaining.days <= settings.ROUND_PROGRESS_WARNING_DAYS:
        progressbar_class = settings.ROUND_PROGRESS_WARNING_CLASS
    else:
        progressbar_class = settings.ROUND_PROGRESS_DEFAULT_CLASS
    percent = 100 * elapsed.days // full.days if full.days > 0 else 100
    context.update(
        {
            "current": current_question,
            "start": start,
            "end": end,
            "full": full,
            "remaining": remaining,
            "elapsed": elapsed,
            "percent": percent,
            "progressbar_class": progressbar_class,
        }
    )
    return context


@register.filter
def progress_time(delta):
    if delta.days >= 1:
        count = delta.days
        return _("%(count)d day", "%(count)d days", count) % {"count": count}
    elif delta.seconds // 3600 >= 1:
        count = delta.seconds // 3600
        return _("%(count)d hour", "%(count)d hours", count) % {"count": count}
    elif delta.seconds // 60 >= 1:
        count = delta.seconds // 60
        return _("%(count)d minute", "%(count)d minutes", count) % {"count": count}
    else:
        count = delta.seconds
        return _("%(count)d second", "%(count)d seconds", count) % {"count": count}


@register.filter
def progress_time_precision(delta):
    if delta.days >= 1:
        return "DAY"
    elif delta.seconds // 3600 >= 1:
        return "HOUR"
    elif delta.seconds // 60 >= 1:
        return "MINUTE"
    else:
        return "SECOND"
