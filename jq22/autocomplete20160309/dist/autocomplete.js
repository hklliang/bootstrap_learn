/**
A jQuery plugin for search hints

Author: Lorenzo Cioni - https://github.com/lorecioni
*/

(function($) {
	$.fn.autocomplete = function(params) {
		var firstKey;
		var hisTime;
		var hisItem;

		function reLoad(value, hisItem, time) {
		
			
			if($.inArray(value, hisItem) >= 0) {

				for(var j = 0; j < localStorage.length; j++) {
					if(value == localStorage.getItem(localStorage.key(j))) {
						localStorage.removeItem(localStorage.key(j));
					}
				}
				localStorage.setItem(time, value);
			}
			//输入的内容localStorage没有记录
			else {
				
				//由于限制了只能有6条记录，所以这里进行判断
				if(hisItem.length >= 3) {
					firstKey = hisTime[0]
					localStorage.removeItem(firstKey);
					localStorage.setItem(time, value);
				} else {
					localStorage.setItem(time, value)
				}
			}
			
			init()
		}

		function init() {
			//每次执行都把2个数组置空
			hisTime = [];

			hisItem = [];
			//本函数内的两个for循环用到的变量

			for(var i = 0; i < localStorage.length; i++) {
				if(!isNaN(localStorage.key(i))) {
					hisItem.unshift(localStorage.getItem(localStorage.key(i)));
					hisTime.push(localStorage.key(i));
				}
			}
		}
		init();

		//Selections
		var currentSelection = -1;
		var currentProposals = [];

		//Default parameters
		params = $.extend({

			placeholder: 'Search',
			width: 200,
			height: 16,
			showButton: true,
			buttonText: 'Search',
			onSubmit: function(text,hisItem) {},
			onBlur: function() {}
		}, params);

		//Build messagess
		this.each(function() {
			//Container
			var searchContainer = $('<div></div>')
				.addClass('autocomplete-container')
				.css('height', params.height * 2);

			//Text input		
			var input = $('<input type="text" autocomplete="off" name="query">')
				.attr('placeholder', params.placeholder)
				.addClass('autocomplete-input')
				.css({
					'width': params.width,
					'height': params.height
				});

			if(params.showButton) {
				input.css('border-radius', '3px 0 0 3px');
			}

			//Proposals
			var proposals = $('<div></div>')
				.addClass('proposal-box')
				.css('width', params.width + 18)
				.css('top', input.height() + 20);
			var proposalList = $('<ul></ul>')
				.addClass('proposal-list');

			proposals.append(proposalList);

			input.keydown(function(e) {
				switch(e.which) {
					case 38: // Up arrow
						e.preventDefault();
						$('ul.proposal-list li').removeClass('selected');
						if((currentSelection - 1) >= 0) {
							currentSelection--;
							$("ul.proposal-list li:eq(" + currentSelection + ")")
								.addClass('selected');
						} else {
							currentSelection = -1;
						}
						break;
					case 40: // Down arrow
						e.preventDefault();
						if((currentSelection + 1) < currentProposals.length) {
							$('ul.proposal-list li').removeClass('selected');
							currentSelection++;
							$("ul.proposal-list li:eq(" + currentSelection + ")")
								.addClass('selected');
						}
						break;
					case 13: // Enter

						if(currentSelection > -1) {
							var text = $("ul.proposal-list li:eq(" + currentSelection + ")").html();
							input.val(text);
						}
						currentSelection = -1;
						proposalList.empty();
						params.onSubmit(input.val(),hisItem);

						reLoad(input.val(), hisItem, (new Date()).getTime())

						break;
					case 27: // Esc button
						currentSelection = -1;
						proposalList.empty();
						input.val('');
						break;
				}
			});
			//不要用change事件，否则失焦事件和点击事件会冲突
			//不要用keyup和paste
			//input表示内容改变时才触发
			input.bind("input", function(e) {
				
				if(e.which != 13 && e.which != 27 &&
					e.which != 38 && e.which != 40) {
					currentProposals = [];
					currentSelection = -1;
					proposalList.empty();
					if(input.val() != '') {
//						var word = "^" + input.val() + ".*";
						var word=$.trim(input.val());
						var reg=new RegExp(word,'i');
						
						proposalList.empty();
						for(var item in hisItem) {
						
							if(reg.test(hisItem[item])) {
							
								currentProposals.push(hisItem[item]);
								var element = $('<li></li>')
									.html(hisItem[item])
									.addClass('proposal')
									.click(function() {
										input.val($(this).html());
										proposalList.empty();
								
										params.onSubmit(input.val(),hisItem);
									})
									.mouseenter(function() {
										$(this).addClass('selected');
									})
									.mouseleave(function() {
										$(this).removeClass('selected');
									});
								proposalList.append(element);
							}
						}
						
						if(proposalList.find('li').length > 0) {
							var removeAll = $('<li>清空历史</li>')
								.addClass('proposal')
								.css({'text-align':'center',
										'backgroundColor':'#bbb'
								})
								.click(function() {
							
									for(var f = 0; f < hisTime.length; f++) {

										localStorage.removeItem(hisTime[f]);

									}
									init();
									proposalList.empty();

								})
								.mouseenter(function() {
									$(this).addClass('selected');
								})
								.mouseleave(function() {
									$(this).removeClass('selected');
								});
							proposalList.append(removeAll);
						
						}

					}
				}
					
			});
			
			input.blur(function(e) {
			
				currentSelection = -1;
				//proposalList.empty();
				params.onBlur();
			});

			searchContainer.append(input);
			searchContainer.append(proposals);

			if(params.showButton) {
				//Search button
				var button = $('<div></div>')
					.addClass('autocomplete-button')
					.html(params.buttonText)
					.css({
						'height': params.height + 2,
						'line-height': params.height + 2 + 'px'
					})
					.click(function() {
						var text = input.val()
						proposalList.empty();
						params.onSubmit(input.val(),hisItem);
						reLoad(text, hisItem, (new Date()).getTime())

					});
				searchContainer.append(button);
			}

			$(this).append(searchContainer);

			if(params.showButton) {
				//Width fix
				searchContainer.css('width', params.width + button.width() + 50);
			}
		});

		return this;
	};

})(jQuery);