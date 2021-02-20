insert into tb_teachers (name, positional_title, profile, avatar_url, create_time, update_time, is_delete) values
('小强墙', '一个孤独患者', '作者简介', '/media/c.jpg', now(), now(), 0);


insert into tb_course_category (name, create_time, update_time, is_delete) values
('python基础', now(), now(), 0),
('python高级', now(), now(), 0),
('python框架', now(), now(), 0);

insert into tb_course (title, cover_url, video_url, `profile`, outline, teacher_id, category_id, create_time,
                       update_time, is_delete) values
('错位时空', 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2F109951165641499081.webp',
 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2FxYagpVrf_3301610698_uhd.mp4',
 '在这么大的世界里，能够遇见你竟然需要如此用力', '穿梭错位的时空，仰望陨落的星辰，你没留下你的名字',1,2,now(),now(), 0),

('大天蓬', 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2F109951164966301138.webp',
 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2FxYagpVrf_3301610698_uhd.mp4',
 '若没有你，那才叫可悲','大天蓬',1,1,now(),now(), 0),
('不舍', 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2FT023R750x750M000004YoNKy0OYmLr.jpg',
 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2Fqmmv_0b6bvqaacaaadaadtmouavpvjlaaagwaaaka.f9844.mp4',
 '动漫和现实中真的有时候表达出来的感觉是一模一样，不管是唐三为了保护小舞而腿骨分离，还是小舞为了唐三献祭自己的灵魂，这些在现实中真的好像，一个男孩子为了让他喜欢了很久很久的一个女孩子活下去也付出了自己的一颗肾，爱情或许就是这样，你在为对方付出的同时对方也在为了你付出着自己的全部，希望有情人终成眷属！','在一段时光一段爱情里，从来都是双向奔赴最有意义，小舞和唐三的爱情在这个需要真正爱情的尘世间弥足可贵。',1,1,now(),now(), 0),

('白月光与朱砂痣', 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2FT056R750x750M000002UCFTT2IkbMN.jpg',
 'https://myboke.cdn.bcebos.com/videoworks%2Fconsole-upload%2F1186997a32aabe0464d879d5ab08952317754f3f.mp4',
'寄予希望却无法拥有的人叫白月光 拥有过却无法再拥抱的人叫朱砂痣', '白月光在照耀，我才想起她的好…', 1,1,now(),now(), 0)



