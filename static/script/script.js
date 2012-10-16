$(document).ready(function() {
    $('#comment-form').submit(submitCommentHandler);
    $('.delete-comment-link').on('click', deleteCommentHandler);
});

// Intercept the form that submits a comment and execute it using AJAX
function submitCommentHandler(event) {
    var postId = getId(this, '.blog-post', 5);
    $.ajax({'url': '/comment/' + postId,
        'type': 'POST',
        'data': {'title': $('#comment-form #id_title').val(),
            'body': $('#comment-form #id_body').val(),
        },
        'beforeSend': function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        'error': function() {
            alert('Failed to add comment. Please ensure form is filled.');
        },
        'success': function(data) {
            node = $(data);
            node.on('click', deleteCommentHandler);
            $('#comments > p').hide();
            node.hide().prependTo('#comments').slideDown();
            $('#comment-form #id_title, #comment-form #id_body').val('');
        },
    });
    event.preventDefault();
}

// Intercept the regular handler for the Delete Comment link and use AJAX
function deleteCommentHandler(event) {
    var postId = getId(this, '.blog-post', 5);
    var commentId = getId(this, '.comment', 8);
    $.ajax({'url': '/delete-comment/' + postId + '/' + commentId,
        'beforeSend': function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        'error': function(xhr) {
            if (xhr.status == 403) {
                alert('This action is not permitted for the current user');
            }
            else {
                alert('Failed to delete comment');
            }
        },
        'success': function(data) {
            var commentId = '#comment-' + data;
            $(commentId).slideUp(400, function() {
                $(commentId).remove(); });
        },
    });
    event.preventDefault();
}

//
// Helper functions
//
function getId(obj, searchClass, prefixLength) {
    return $(obj).parents(searchClass).attr('id').substr(prefixLength);
}

// Disclosure: The following function was copied and pasted verbatim!
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
