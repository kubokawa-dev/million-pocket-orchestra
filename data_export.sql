--
-- PostgreSQL database dump
--

\restrict GDrkXE2RaVNkmYoSYwWRBf87nLtmqzcpbLVe7UMInD09cPvEV5ce5oBmML5oPDo

-- Dumped from database version 14.19 (Debian 14.19-1.pgdg13+1)
-- Dumped by pg_dump version 14.19 (Debian 14.19-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: _prisma_migrations; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public._prisma_migrations VALUES ('d89304c1-74c3-42f5-b50d-6d9f5c620e34', '2af56717165b8c4bcff232845b0565ceb21ec91ec8e92ee16a6854ab52e6899f', '2025-10-18 04:49:47.70151+00', '20251016155543_init', NULL, NULL, '2025-10-18 04:49:47.582798+00', 1);
INSERT INTO public._prisma_migrations VALUES ('7dddf1cf-3ec8-4b41-95ce-9059fedca7e0', '1e72e3d6974c811972168cfb376618b847d89e444df7ba14f70d0d04ddf22704', '2025-10-18 04:49:47.825297+00', 'add_prediction_history', NULL, NULL, '2025-10-18 04:49:47.707879+00', 1);
INSERT INTO public._prisma_migrations VALUES ('22a03828-3208-4f0c-a9f1-775dcd35d8db', 'bdfe2da10c1622314066ae864771e046961496a382c8d302660bc110356afd9d', '2025-10-18 04:49:47.86245+00', 'add_target_draw_to_prediction_log', NULL, NULL, '2025-10-18 04:49:47.831146+00', 1);
INSERT INTO public._prisma_migrations VALUES ('34f6bc48-9ee7-4416-9b4b-7e355ab38032', 'e566a63cf6d2246d96fa3cdb798760a9c410ff7d1aff44385f2690ee343fc6ed', '2025-10-18 04:51:22.250837+00', '20251018045122_add_numbers3_draws', NULL, NULL, '2025-10-18 04:51:22.238158+00', 1);
INSERT INTO public._prisma_migrations VALUES ('7f9d63ea-535b-41a3-b676-77311c1cacb4', 'af77559451354468649be994472c29dac0d2ff869a1a916386c2ab089ad43ea0', '2025-10-18 05:41:44.317245+00', '20251018054144_add_numbers3_prediction_tables', NULL, NULL, '2025-10-18 05:41:44.269741+00', 1);
INSERT INTO public._prisma_migrations VALUES ('b5bb94e3-07aa-4f9c-9d57-a4588b340ca6', 'c56e69afae43ba7add667bb98b4b32a4e665adf1690ebdee287fe33bfe5185a8', '2025-10-18 05:53:06.150613+00', '20251018055306_add_loto6_prediction_tables', NULL, NULL, '2025-10-18 05:53:06.100622+00', 1);


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: user
--



--
-- Data for Name: predictions; Type: TABLE DATA; Schema: public; Owner: user
--



--
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: user
--



--
-- Data for Name: likes; Type: TABLE DATA; Schema: public; Owner: user
--



--
-- Data for Name: loto6_draws; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.loto6_draws VALUES (1962, '2025/01/06', '4,8,19,22,32,37', 26);
INSERT INTO public.loto6_draws VALUES (1963, '2025/01/09', '3,4,20,29,35,38', 6);
INSERT INTO public.loto6_draws VALUES (1964, '2025/01/13', '2,5,28,33,35,36', 34);
INSERT INTO public.loto6_draws VALUES (1965, '2025/01/16', '17,18,20,23,33,43', 19);
INSERT INTO public.loto6_draws VALUES (1966, '2025/01/20', '4,12,25,29,34,36', 32);
INSERT INTO public.loto6_draws VALUES (1967, '2025/01/23', '3,4,22,26,29,35', 37);
INSERT INTO public.loto6_draws VALUES (1968, '2025/01/27', '6,13,15,22,35,41', 37);
INSERT INTO public.loto6_draws VALUES (1969, '2025/01/30', '3,7,12,13,35,38', 24);
INSERT INTO public.loto6_draws VALUES (1970, '2025/02/03', '11,26,27,31,36,37', 42);
INSERT INTO public.loto6_draws VALUES (1971, '2025/02/06', '2,6,9,26,32,36', 23);
INSERT INTO public.loto6_draws VALUES (1972, '2025/02/10', '3,14,27,28,32,36', 12);
INSERT INTO public.loto6_draws VALUES (1973, '2025/02/13', '7,10,14,27,28,32', 4);
INSERT INTO public.loto6_draws VALUES (1974, '2025/02/17', '2,6,13,21,24,30', 43);
INSERT INTO public.loto6_draws VALUES (1975, '2025/02/20', '11,13,15,20,35,42', 19);
INSERT INTO public.loto6_draws VALUES (1976, '2025/02/24', '4,6,22,30,33,36', 2);
INSERT INTO public.loto6_draws VALUES (1977, '2025/02/27', '4,14,20,28,29,34', 30);
INSERT INTO public.loto6_draws VALUES (1978, '2025/03/03', '23,25,26,30,34,35', 12);
INSERT INTO public.loto6_draws VALUES (1979, '2025/03/06', '15,18,19,21,37,40', 17);
INSERT INTO public.loto6_draws VALUES (1980, '2025/03/10', '1,2,13,19,35,41', 3);
INSERT INTO public.loto6_draws VALUES (1981, '2025/03/13', '5,10,15,17,29,41', 30);
INSERT INTO public.loto6_draws VALUES (1982, '2025/03/17', '20,21,23,28,32,34', 6);
INSERT INTO public.loto6_draws VALUES (1983, '2025/03/20', '3,18,31,36,37,40', 23);
INSERT INTO public.loto6_draws VALUES (1984, '2025/03/24', '4,19,28,29,34,40', 3);
INSERT INTO public.loto6_draws VALUES (1985, '2025/03/27', '1,30,36,37,41,43', 33);
INSERT INTO public.loto6_draws VALUES (1986, '2025/03/31', '14,20,29,31,41,42', 24);
INSERT INTO public.loto6_draws VALUES (1987, '2025/04/03', '8,12,25,28,32,42', 27);
INSERT INTO public.loto6_draws VALUES (1988, '2025/04/07', '6,20,23,24,33,35', 27);
INSERT INTO public.loto6_draws VALUES (1989, '2025/04/10', '15,17,23,29,35,43', 8);
INSERT INTO public.loto6_draws VALUES (1990, '2025/04/14', '6,9,15,19,24,40', 30);
INSERT INTO public.loto6_draws VALUES (1991, '2025/04/17', '1,5,12,16,17,40', 4);
INSERT INTO public.loto6_draws VALUES (1992, '2025/04/21', '9,11,18,21,27,34', 13);
INSERT INTO public.loto6_draws VALUES (1993, '2025/04/24', '7,12,13,35,37,42', 31);
INSERT INTO public.loto6_draws VALUES (1994, '2025/04/28', '10,11,13,16,24,26', 12);
INSERT INTO public.loto6_draws VALUES (1995, '2025/05/01', '2,4,8,26,27,37', 19);
INSERT INTO public.loto6_draws VALUES (1996, '2025/05/05', '6,17,26,28,33,34', 20);
INSERT INTO public.loto6_draws VALUES (1997, '2025/05/08', '5,16,17,28,36,40', 14);
INSERT INTO public.loto6_draws VALUES (1998, '2025/05/12', '1,4,6,9,20,43', 21);
INSERT INTO public.loto6_draws VALUES (1999, '2025/05/15', '17,31,34,35,36,38', 2);
INSERT INTO public.loto6_draws VALUES (2000, '2025/05/19', '1,2,16,21,25,35', 22);
INSERT INTO public.loto6_draws VALUES (2001, '2025/05/22', '13,21,24,26,34,36', 20);
INSERT INTO public.loto6_draws VALUES (2002, '2025/05/26', '1,17,19,23,36,42', 15);
INSERT INTO public.loto6_draws VALUES (2003, '2025/05/29', '1,5,10,13,35,40', 39);
INSERT INTO public.loto6_draws VALUES (2004, '2025/06/02', '16,18,25,27,31,36', 7);
INSERT INTO public.loto6_draws VALUES (2005, '2025/06/05', '3,7,18,27,33,34', 6);
INSERT INTO public.loto6_draws VALUES (2006, '2025/06/09', '4,7,19,22,26,28', 33);
INSERT INTO public.loto6_draws VALUES (2007, '2025/06/12', '6,18,23,24,30,35', 38);
INSERT INTO public.loto6_draws VALUES (2008, '2025/06/16', '5,8,9,17,22,36', 30);
INSERT INTO public.loto6_draws VALUES (2009, '2025/06/19', '8,17,20,35,36,40', 12);
INSERT INTO public.loto6_draws VALUES (2010, '2025/06/23', '9,15,24,29,31,40', 13);
INSERT INTO public.loto6_draws VALUES (2011, '2025/06/26', '12,14,18,24,30,42', 4);
INSERT INTO public.loto6_draws VALUES (2012, '2025/06/30', '1,14,20,36,38,41', 30);
INSERT INTO public.loto6_draws VALUES (2013, '2025/07/03', '7,12,30,31,39,43', 42);
INSERT INTO public.loto6_draws VALUES (2014, '2025/07/07', '7,11,21,24,29,34', 40);
INSERT INTO public.loto6_draws VALUES (2015, '2025/07/10', '6,8,13,16,20,23', 26);
INSERT INTO public.loto6_draws VALUES (2016, '2025/07/14', '10,13,27,31,40,42', 1);
INSERT INTO public.loto6_draws VALUES (2017, '2025/07/17', '2,4,11,22,24,35', 8);
INSERT INTO public.loto6_draws VALUES (2018, '2025/07/21', '1,2,14,21,22,33', 37);
INSERT INTO public.loto6_draws VALUES (2019, '2025/07/24', '7,13,14,21,39,42', 9);
INSERT INTO public.loto6_draws VALUES (2020, '2025/07/28', '5,21,23,28,38,39', 32);
INSERT INTO public.loto6_draws VALUES (2021, '2025/07/31', '2,17,22,29,30,43', 31);
INSERT INTO public.loto6_draws VALUES (2030, '2025/09/01', '3,7,28,29,32,36', 13);
INSERT INTO public.loto6_draws VALUES (2031, '2025/09/04', '2,3,16,20,23,29', 27);
INSERT INTO public.loto6_draws VALUES (2032, '2025/09/08', '8,15,27,33,37,39', 31);
INSERT INTO public.loto6_draws VALUES (2033, '2025/09/11', '5,16,21,22,33,35', 26);
INSERT INTO public.loto6_draws VALUES (2034, '2025/09/15', '2,13,22,25,35,37', 17);
INSERT INTO public.loto6_draws VALUES (2035, '2025/09/18', '5,10,12,17,21,35', 9);
INSERT INTO public.loto6_draws VALUES (2036, '2025/09/22', '7,10,17,26,35,42', 33);
INSERT INTO public.loto6_draws VALUES (2037, '2025/09/25', '7,12,20,23,27,29', 10);
INSERT INTO public.loto6_draws VALUES (2038, '2025/09/29', '5,31,37,39,41,42', 33);
INSERT INTO public.loto6_draws VALUES (2039, '2025/10/02', '2,15,25,27,38,42', 22);
INSERT INTO public.loto6_draws VALUES (2040, '2025/10/06', '7,12,14,15,24,30', 32);
INSERT INTO public.loto6_draws VALUES (2041, '2025/10/09', '4,19,22,24,32,38', 11);
INSERT INTO public.loto6_draws VALUES (2042, '2025/10/13', '9,14,29,38,41,43', 12);
INSERT INTO public.loto6_draws VALUES (2043, '2025/10/16', '11,19,22,34,40,42', 31);


--
-- Data for Name: loto6_ensemble_predictions; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.loto6_ensemble_predictions VALUES (2, '2025-10-18 06:02:07.026', 2044, '2025-10-18T06:02:06.986378+00:00', 8, '{"frequency_weight": 0.25, "position_weight": 0.25, "pattern_weight": 0.25, "recent_weight": 0.25}', 10, '[{"number": "123456", "score": 0.95}, {"number": "234567", "score": 0.92}, {"number": "345678", "score": 0.88}, {"number": "456789", "score": 0.85}, {"number": "567890", "score": 0.82}, {"number": "678901", "score": 0.79}, {"number": "789012", "score": 0.76}, {"number": "890123", "score": 0.73}, {"number": "901234", "score": 0.7}, {"number": "012345", "score": 0.67}]', '{"frequency_model": ["123456", "234567", "345678", "456789", "567890"], "position_model": ["234567", "345678", "456789", "567890", "678901"], "pattern_model": ["123456", "456789", "567890", "678901", "789012"], "recent_model": ["345678", "567890", "678901", "789012", "890123"]}', NULL, NULL, NULL, NULL, NULL, NULL, 'アンサンブル予測（10候補）');
INSERT INTO public.loto6_ensemble_predictions VALUES (1, '2025-10-18 06:00:34.086', 2044, '2025-10-18T06:00:34.066164+00:00', 8, '{"frequency_weight": 0.25, "position_weight": 0.25, "pattern_weight": 0.25, "recent_weight": 0.25}', 10, '[{"number": "123456", "score": 0.95}, {"number": "234567", "score": 0.92}, {"number": "345678", "score": 0.88}, {"number": "456789", "score": 0.85}, {"number": "567890", "score": 0.82}, {"number": "678901", "score": 0.79}, {"number": "789012", "score": 0.76}, {"number": "890123", "score": 0.73}, {"number": "901234", "score": 0.7}, {"number": "012345", "score": 0.67}]', '{"frequency_model": ["123456", "234567", "345678", "456789", "567890"], "position_model": ["234567", "345678", "456789", "567890", "678901"], "pattern_model": ["123456", "456789", "567890", "678901", "789012"], "recent_model": ["345678", "567890", "678901", "789012", "890123"]}', 2044, '123456', 7, 'exact', 6, true, '結果更新: 123456 (的中: 6/6桁), ボーナス数字7的中, 最良予測: 123456');


--
-- Data for Name: loto6_model_events; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.loto6_model_events VALUES (1, '2025-10-18T06:00:34.138906+00:00', '123456', '["123456", "234567", "345678", "456789", "567890"]', 1, '123456', 6, 'テスト用の学習イベント');
INSERT INTO public.loto6_model_events VALUES (2, '2025-10-18T06:02:07.055331+00:00', '123456', '["123456", "234567", "345678", "456789", "567890"]', 1, '123456', 6, 'テスト用の学習イベント');


--
-- Data for Name: loto6_prediction_candidates; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.loto6_prediction_candidates VALUES (1, 1, 1, '123456', 0.95, '["frequency_model", "pattern_model"]', '2025-10-18 06:00:34.089');
INSERT INTO public.loto6_prediction_candidates VALUES (2, 1, 2, '234567', 0.92, '["frequency_model", "position_model"]', '2025-10-18 06:00:34.091');
INSERT INTO public.loto6_prediction_candidates VALUES (3, 1, 3, '345678', 0.88, '["frequency_model", "position_model", "recent_model"]', '2025-10-18 06:00:34.092');
INSERT INTO public.loto6_prediction_candidates VALUES (4, 1, 4, '456789', 0.85, '["frequency_model", "position_model", "pattern_model"]', '2025-10-18 06:00:34.093');
INSERT INTO public.loto6_prediction_candidates VALUES (5, 1, 5, '567890', 0.82, '["frequency_model", "position_model", "pattern_model", "recent_model"]', '2025-10-18 06:00:34.094');
INSERT INTO public.loto6_prediction_candidates VALUES (6, 1, 6, '678901', 0.79, '["position_model", "pattern_model", "recent_model"]', '2025-10-18 06:00:34.095');
INSERT INTO public.loto6_prediction_candidates VALUES (7, 1, 7, '789012', 0.76, '["pattern_model", "recent_model"]', '2025-10-18 06:00:34.095');
INSERT INTO public.loto6_prediction_candidates VALUES (8, 1, 8, '890123', 0.73, '["recent_model"]', '2025-10-18 06:00:34.096');
INSERT INTO public.loto6_prediction_candidates VALUES (9, 1, 9, '901234', 0.7, '[]', '2025-10-18 06:00:34.097');
INSERT INTO public.loto6_prediction_candidates VALUES (10, 1, 10, '012345', 0.67, '[]', '2025-10-18 06:00:34.098');
INSERT INTO public.loto6_prediction_candidates VALUES (11, 2, 1, '123456', 0.95, '["frequency_model", "pattern_model"]', '2025-10-18 06:02:07.027');
INSERT INTO public.loto6_prediction_candidates VALUES (12, 2, 2, '234567', 0.92, '["frequency_model", "position_model"]', '2025-10-18 06:02:07.028');
INSERT INTO public.loto6_prediction_candidates VALUES (13, 2, 3, '345678', 0.88, '["frequency_model", "position_model", "recent_model"]', '2025-10-18 06:02:07.029');
INSERT INTO public.loto6_prediction_candidates VALUES (14, 2, 4, '456789', 0.85, '["frequency_model", "position_model", "pattern_model"]', '2025-10-18 06:02:07.03');
INSERT INTO public.loto6_prediction_candidates VALUES (15, 2, 5, '567890', 0.82, '["frequency_model", "position_model", "pattern_model", "recent_model"]', '2025-10-18 06:02:07.031');
INSERT INTO public.loto6_prediction_candidates VALUES (16, 2, 6, '678901', 0.79, '["position_model", "pattern_model", "recent_model"]', '2025-10-18 06:02:07.031');
INSERT INTO public.loto6_prediction_candidates VALUES (17, 2, 7, '789012', 0.76, '["pattern_model", "recent_model"]', '2025-10-18 06:02:07.031');
INSERT INTO public.loto6_prediction_candidates VALUES (18, 2, 8, '890123', 0.73, '["recent_model"]', '2025-10-18 06:02:07.033');
INSERT INTO public.loto6_prediction_candidates VALUES (19, 2, 9, '901234', 0.7, '[]', '2025-10-18 06:02:07.034');
INSERT INTO public.loto6_prediction_candidates VALUES (20, 2, 10, '012345', 0.67, '[]', '2025-10-18 06:02:07.034');


--
-- Data for Name: loto6_predictions_log; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.loto6_predictions_log VALUES (1, '2025-10-18T06:00:34.098693+00:00', 'ensemble_prediction', '予測1位', '123456', 2044);
INSERT INTO public.loto6_predictions_log VALUES (2, '2025-10-18T06:00:34.099235+00:00', 'ensemble_prediction', '予測2位', '234567', 2044);
INSERT INTO public.loto6_predictions_log VALUES (3, '2025-10-18T06:00:34.100288+00:00', 'ensemble_prediction', '予測3位', '345678', 2044);
INSERT INTO public.loto6_predictions_log VALUES (4, '2025-10-18T06:00:34.100805+00:00', 'ensemble_prediction', '予測4位', '456789', 2044);
INSERT INTO public.loto6_predictions_log VALUES (5, '2025-10-18T06:00:34.100805+00:00', 'ensemble_prediction', '予測5位', '567890', 2044);
INSERT INTO public.loto6_predictions_log VALUES (6, '2025-10-18T06:00:34.101813+00:00', 'ensemble_prediction', '予測6位', '678901', 2044);
INSERT INTO public.loto6_predictions_log VALUES (7, '2025-10-18T06:00:34.101813+00:00', 'ensemble_prediction', '予測7位', '789012', 2044);
INSERT INTO public.loto6_predictions_log VALUES (8, '2025-10-18T06:00:34.102956+00:00', 'ensemble_prediction', '予測8位', '890123', 2044);
INSERT INTO public.loto6_predictions_log VALUES (9, '2025-10-18T06:00:34.103560+00:00', 'ensemble_prediction', '予測9位', '901234', 2044);
INSERT INTO public.loto6_predictions_log VALUES (10, '2025-10-18T06:00:34.104569+00:00', 'ensemble_prediction', '予測10位', '012345', 2044);
INSERT INTO public.loto6_predictions_log VALUES (11, '2025-10-18T06:02:07.034886+00:00', 'ensemble_prediction', '予測1位', '123456', 2044);
INSERT INTO public.loto6_predictions_log VALUES (12, '2025-10-18T06:02:07.035886+00:00', 'ensemble_prediction', '予測2位', '234567', 2044);
INSERT INTO public.loto6_predictions_log VALUES (13, '2025-10-18T06:02:07.035886+00:00', 'ensemble_prediction', '予測3位', '345678', 2044);
INSERT INTO public.loto6_predictions_log VALUES (14, '2025-10-18T06:02:07.036886+00:00', 'ensemble_prediction', '予測4位', '456789', 2044);
INSERT INTO public.loto6_predictions_log VALUES (15, '2025-10-18T06:02:07.037888+00:00', 'ensemble_prediction', '予測5位', '567890', 2044);
INSERT INTO public.loto6_predictions_log VALUES (16, '2025-10-18T06:02:07.037888+00:00', 'ensemble_prediction', '予測6位', '678901', 2044);
INSERT INTO public.loto6_predictions_log VALUES (17, '2025-10-18T06:02:07.037888+00:00', 'ensemble_prediction', '予測7位', '789012', 2044);
INSERT INTO public.loto6_predictions_log VALUES (18, '2025-10-18T06:02:07.039394+00:00', 'ensemble_prediction', '予測8位', '890123', 2044);
INSERT INTO public.loto6_predictions_log VALUES (19, '2025-10-18T06:02:07.039902+00:00', 'ensemble_prediction', '予測9位', '901234', 2044);
INSERT INTO public.loto6_predictions_log VALUES (20, '2025-10-18T06:02:07.040912+00:00', 'ensemble_prediction', '予測10位', '012345', 2044);


--
-- Data for Name: numbers3_draws; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers3_draws VALUES (1, '2025/01/06', '188');
INSERT INTO public.numbers3_draws VALUES (2, '2025/01/07', '238');
INSERT INTO public.numbers3_draws VALUES (3, '2025/01/08', '462');
INSERT INTO public.numbers3_draws VALUES (4, '2025/01/09', '207');
INSERT INTO public.numbers3_draws VALUES (5, '2025/01/10', '669');
INSERT INTO public.numbers3_draws VALUES (6, '2025/01/13', '265');
INSERT INTO public.numbers3_draws VALUES (7, '2025/01/14', '606');
INSERT INTO public.numbers3_draws VALUES (8, '2025/01/15', '216');
INSERT INTO public.numbers3_draws VALUES (9, '2025/01/16', '100');
INSERT INTO public.numbers3_draws VALUES (10, '2025/01/17', '944');
INSERT INTO public.numbers3_draws VALUES (11, '2025/01/20', '672');
INSERT INTO public.numbers3_draws VALUES (12, '2025/01/21', '496');
INSERT INTO public.numbers3_draws VALUES (13, '2025/01/22', '842');
INSERT INTO public.numbers3_draws VALUES (14, '2025/01/23', '239');
INSERT INTO public.numbers3_draws VALUES (15, '2025/01/24', '557');
INSERT INTO public.numbers3_draws VALUES (16, '2025/01/27', '169');
INSERT INTO public.numbers3_draws VALUES (17, '2025/01/28', '763');
INSERT INTO public.numbers3_draws VALUES (18, '2025/01/29', '314');
INSERT INTO public.numbers3_draws VALUES (19, '2025/01/30', '577');
INSERT INTO public.numbers3_draws VALUES (20, '2025/01/31', '020');
INSERT INTO public.numbers3_draws VALUES (26, '2025/02/03', '168');
INSERT INTO public.numbers3_draws VALUES (27, '2025/02/04', '799');
INSERT INTO public.numbers3_draws VALUES (28, '2025/02/05', '973');
INSERT INTO public.numbers3_draws VALUES (29, '2025/02/06', '033');
INSERT INTO public.numbers3_draws VALUES (30, '2025/02/07', '100');
INSERT INTO public.numbers3_draws VALUES (31, '2025/02/10', '249');
INSERT INTO public.numbers3_draws VALUES (32, '2025/02/11', '086');
INSERT INTO public.numbers3_draws VALUES (33, '2025/02/12', '427');
INSERT INTO public.numbers3_draws VALUES (34, '2025/02/13', '354');
INSERT INTO public.numbers3_draws VALUES (35, '2025/02/14', '720');
INSERT INTO public.numbers3_draws VALUES (36, '2025/02/17', '796');
INSERT INTO public.numbers3_draws VALUES (37, '2025/02/18', '804');
INSERT INTO public.numbers3_draws VALUES (38, '2025/02/19', '157');
INSERT INTO public.numbers3_draws VALUES (39, '2025/02/20', '770');
INSERT INTO public.numbers3_draws VALUES (40, '2025/02/21', '531');
INSERT INTO public.numbers3_draws VALUES (41, '2025/02/24', '423');
INSERT INTO public.numbers3_draws VALUES (42, '2025/02/25', '185');
INSERT INTO public.numbers3_draws VALUES (43, '2025/02/26', '996');
INSERT INTO public.numbers3_draws VALUES (44, '2025/02/27', '372');
INSERT INTO public.numbers3_draws VALUES (45, '2025/02/28', '394');
INSERT INTO public.numbers3_draws VALUES (51, '2025/03/03', '422');
INSERT INTO public.numbers3_draws VALUES (52, '2025/03/04', '638');
INSERT INTO public.numbers3_draws VALUES (53, '2025/03/05', '052');
INSERT INTO public.numbers3_draws VALUES (54, '2025/03/06', '417');
INSERT INTO public.numbers3_draws VALUES (55, '2025/03/07', '128');
INSERT INTO public.numbers3_draws VALUES (56, '2025/03/10', '959');
INSERT INTO public.numbers3_draws VALUES (57, '2025/03/11', '036');
INSERT INTO public.numbers3_draws VALUES (58, '2025/03/12', '312');
INSERT INTO public.numbers3_draws VALUES (59, '2025/03/13', '946');
INSERT INTO public.numbers3_draws VALUES (60, '2025/03/14', '766');
INSERT INTO public.numbers3_draws VALUES (61, '2025/03/17', '187');
INSERT INTO public.numbers3_draws VALUES (62, '2025/03/18', '150');
INSERT INTO public.numbers3_draws VALUES (63, '2025/03/19', '099');
INSERT INTO public.numbers3_draws VALUES (64, '2025/03/20', '320');
INSERT INTO public.numbers3_draws VALUES (65, '2025/03/21', '146');
INSERT INTO public.numbers3_draws VALUES (66, '2025/03/24', '948');
INSERT INTO public.numbers3_draws VALUES (67, '2025/03/25', '990');
INSERT INTO public.numbers3_draws VALUES (68, '2025/03/26', '029');
INSERT INTO public.numbers3_draws VALUES (69, '2025/03/27', '725');
INSERT INTO public.numbers3_draws VALUES (70, '2025/03/28', '730');
INSERT INTO public.numbers3_draws VALUES (71, '2025/03/31', '337');
INSERT INTO public.numbers3_draws VALUES (76, '2025/04/01', '515');
INSERT INTO public.numbers3_draws VALUES (77, '2025/04/02', '964');
INSERT INTO public.numbers3_draws VALUES (78, '2025/04/03', '129');
INSERT INTO public.numbers3_draws VALUES (79, '2025/04/04', '214');
INSERT INTO public.numbers3_draws VALUES (80, '2025/04/07', '623');
INSERT INTO public.numbers3_draws VALUES (81, '2025/04/08', '457');
INSERT INTO public.numbers3_draws VALUES (82, '2025/04/09', '046');
INSERT INTO public.numbers3_draws VALUES (83, '2025/04/10', '467');
INSERT INTO public.numbers3_draws VALUES (84, '2025/04/11', '543');
INSERT INTO public.numbers3_draws VALUES (85, '2025/04/14', '313');
INSERT INTO public.numbers3_draws VALUES (86, '2025/04/15', '574');
INSERT INTO public.numbers3_draws VALUES (87, '2025/04/16', '629');
INSERT INTO public.numbers3_draws VALUES (88, '2025/04/17', '249');
INSERT INTO public.numbers3_draws VALUES (89, '2025/04/18', '440');
INSERT INTO public.numbers3_draws VALUES (90, '2025/04/21', '637');
INSERT INTO public.numbers3_draws VALUES (91, '2025/04/22', '020');
INSERT INTO public.numbers3_draws VALUES (92, '2025/04/23', '896');
INSERT INTO public.numbers3_draws VALUES (93, '2025/04/24', '978');
INSERT INTO public.numbers3_draws VALUES (94, '2025/04/25', '446');
INSERT INTO public.numbers3_draws VALUES (95, '2025/04/28', '718');
INSERT INTO public.numbers3_draws VALUES (96, '2025/04/29', '253');
INSERT INTO public.numbers3_draws VALUES (97, '2025/04/30', '878');
INSERT INTO public.numbers3_draws VALUES (101, '2025/05/01', '752');
INSERT INTO public.numbers3_draws VALUES (102, '2025/05/02', '652');
INSERT INTO public.numbers3_draws VALUES (103, '2025/05/05', '133');
INSERT INTO public.numbers3_draws VALUES (104, '2025/05/06', '157');
INSERT INTO public.numbers3_draws VALUES (105, '2025/05/07', '990');
INSERT INTO public.numbers3_draws VALUES (106, '2025/05/08', '990');
INSERT INTO public.numbers3_draws VALUES (107, '2025/05/09', '190');
INSERT INTO public.numbers3_draws VALUES (108, '2025/05/12', '502');
INSERT INTO public.numbers3_draws VALUES (109, '2025/05/13', '152');
INSERT INTO public.numbers3_draws VALUES (110, '2025/05/14', '122');
INSERT INTO public.numbers3_draws VALUES (111, '2025/05/15', '371');
INSERT INTO public.numbers3_draws VALUES (112, '2025/05/16', '611');
INSERT INTO public.numbers3_draws VALUES (113, '2025/05/19', '870');
INSERT INTO public.numbers3_draws VALUES (114, '2025/05/20', '263');
INSERT INTO public.numbers3_draws VALUES (115, '2025/05/21', '355');
INSERT INTO public.numbers3_draws VALUES (116, '2025/05/22', '680');
INSERT INTO public.numbers3_draws VALUES (117, '2025/05/23', '752');
INSERT INTO public.numbers3_draws VALUES (118, '2025/05/26', '902');
INSERT INTO public.numbers3_draws VALUES (119, '2025/05/27', '238');
INSERT INTO public.numbers3_draws VALUES (120, '2025/05/28', '564');
INSERT INTO public.numbers3_draws VALUES (121, '2025/05/29', '849');
INSERT INTO public.numbers3_draws VALUES (122, '2025/05/30', '549');
INSERT INTO public.numbers3_draws VALUES (126, '2025/06/02', '898');
INSERT INTO public.numbers3_draws VALUES (127, '2025/06/03', '800');
INSERT INTO public.numbers3_draws VALUES (128, '2025/06/04', '819');
INSERT INTO public.numbers3_draws VALUES (129, '2025/06/05', '066');
INSERT INTO public.numbers3_draws VALUES (130, '2025/06/06', '227');
INSERT INTO public.numbers3_draws VALUES (131, '2025/06/09', '490');
INSERT INTO public.numbers3_draws VALUES (132, '2025/06/10', '284');
INSERT INTO public.numbers3_draws VALUES (133, '2025/06/11', '918');
INSERT INTO public.numbers3_draws VALUES (134, '2025/06/12', '535');
INSERT INTO public.numbers3_draws VALUES (135, '2025/06/13', '069');
INSERT INTO public.numbers3_draws VALUES (136, '2025/06/16', '040');
INSERT INTO public.numbers3_draws VALUES (137, '2025/06/17', '482');
INSERT INTO public.numbers3_draws VALUES (138, '2025/06/18', '120');
INSERT INTO public.numbers3_draws VALUES (139, '2025/06/19', '695');
INSERT INTO public.numbers3_draws VALUES (140, '2025/06/20', '536');
INSERT INTO public.numbers3_draws VALUES (141, '2025/06/23', '870');
INSERT INTO public.numbers3_draws VALUES (142, '2025/06/24', '652');
INSERT INTO public.numbers3_draws VALUES (143, '2025/06/25', '306');
INSERT INTO public.numbers3_draws VALUES (144, '2025/06/26', '458');
INSERT INTO public.numbers3_draws VALUES (145, '2025/06/27', '621');
INSERT INTO public.numbers3_draws VALUES (146, '2025/06/30', '149');
INSERT INTO public.numbers3_draws VALUES (151, '2025/07/01', '307');
INSERT INTO public.numbers3_draws VALUES (152, '2025/07/02', '897');
INSERT INTO public.numbers3_draws VALUES (153, '2025/07/03', '108');
INSERT INTO public.numbers3_draws VALUES (154, '2025/07/04', '407');
INSERT INTO public.numbers3_draws VALUES (155, '2025/07/07', '190');
INSERT INTO public.numbers3_draws VALUES (156, '2025/07/08', '614');
INSERT INTO public.numbers3_draws VALUES (157, '2025/07/09', '843');
INSERT INTO public.numbers3_draws VALUES (158, '2025/07/10', '364');
INSERT INTO public.numbers3_draws VALUES (159, '2025/07/11', '324');
INSERT INTO public.numbers3_draws VALUES (160, '2025/07/14', '588');
INSERT INTO public.numbers3_draws VALUES (161, '2025/07/15', '548');
INSERT INTO public.numbers3_draws VALUES (162, '2025/07/16', '693');
INSERT INTO public.numbers3_draws VALUES (163, '2025/07/17', '442');
INSERT INTO public.numbers3_draws VALUES (164, '2025/07/18', '601');
INSERT INTO public.numbers3_draws VALUES (165, '2025/07/21', '224');
INSERT INTO public.numbers3_draws VALUES (166, '2025/07/22', '168');
INSERT INTO public.numbers3_draws VALUES (167, '2025/07/23', '801');
INSERT INTO public.numbers3_draws VALUES (168, '2025/07/24', '671');
INSERT INTO public.numbers3_draws VALUES (169, '2025/07/25', '294');
INSERT INTO public.numbers3_draws VALUES (170, '2025/07/28', '648');
INSERT INTO public.numbers3_draws VALUES (171, '2025/07/29', '524');
INSERT INTO public.numbers3_draws VALUES (172, '2025/07/30', '491');
INSERT INTO public.numbers3_draws VALUES (173, '2025/07/31', '244');
INSERT INTO public.numbers3_draws VALUES (6783, '2025/08/04', '856');
INSERT INTO public.numbers3_draws VALUES (6784, '2025/08/05', '361');
INSERT INTO public.numbers3_draws VALUES (6785, '2025/08/06', '300');
INSERT INTO public.numbers3_draws VALUES (6786, '2025/08/07', '207');
INSERT INTO public.numbers3_draws VALUES (6787, '2025/08/08', '657');
INSERT INTO public.numbers3_draws VALUES (6788, '2025/08/11', '090');
INSERT INTO public.numbers3_draws VALUES (6789, '2025/08/12', '462');
INSERT INTO public.numbers3_draws VALUES (6790, '2025/08/13', '766');
INSERT INTO public.numbers3_draws VALUES (6791, '2025/08/14', '142');
INSERT INTO public.numbers3_draws VALUES (6792, '2025/08/15', '486');
INSERT INTO public.numbers3_draws VALUES (6793, '2025/08/18', '776');
INSERT INTO public.numbers3_draws VALUES (6794, '2025/08/19', '631');
INSERT INTO public.numbers3_draws VALUES (6795, '2025/08/20', '218');
INSERT INTO public.numbers3_draws VALUES (6796, '2025/08/21', '741');
INSERT INTO public.numbers3_draws VALUES (6797, '2025/08/22', '461');
INSERT INTO public.numbers3_draws VALUES (6798, '2025/08/25', '313');
INSERT INTO public.numbers3_draws VALUES (6799, '2025/08/26', '650');
INSERT INTO public.numbers3_draws VALUES (6800, '2025/08/27', '038');
INSERT INTO public.numbers3_draws VALUES (6801, '2025/08/28', '186');
INSERT INTO public.numbers3_draws VALUES (6802, '2025/08/29', '805');
INSERT INTO public.numbers3_draws VALUES (6804, '2025/09/02', '275');
INSERT INTO public.numbers3_draws VALUES (6805, '2025/09/03', '806');
INSERT INTO public.numbers3_draws VALUES (6806, '2025/09/04', '131');
INSERT INTO public.numbers3_draws VALUES (6807, '2025/09/05', '856');
INSERT INTO public.numbers3_draws VALUES (6808, '2025/09/08', '572');
INSERT INTO public.numbers3_draws VALUES (6809, '2025/09/09', '891');
INSERT INTO public.numbers3_draws VALUES (6810, '2025/09/10', '777');
INSERT INTO public.numbers3_draws VALUES (6811, '2025/09/11', '827');
INSERT INTO public.numbers3_draws VALUES (6812, '2025/09/12', '411');
INSERT INTO public.numbers3_draws VALUES (6813, '2025/09/15', '573');
INSERT INTO public.numbers3_draws VALUES (6814, '2025/09/16', '672');
INSERT INTO public.numbers3_draws VALUES (6815, '2025/09/17', '578');
INSERT INTO public.numbers3_draws VALUES (6816, '2025/09/18', '368');
INSERT INTO public.numbers3_draws VALUES (6817, '2025/09/19', '630');
INSERT INTO public.numbers3_draws VALUES (6818, '2025/09/22', '064');
INSERT INTO public.numbers3_draws VALUES (6819, '2025/09/23', '072');
INSERT INTO public.numbers3_draws VALUES (6820, '2025/09/24', '055');
INSERT INTO public.numbers3_draws VALUES (6821, '2025/09/25', '439');
INSERT INTO public.numbers3_draws VALUES (6822, '2025/09/26', '049');
INSERT INTO public.numbers3_draws VALUES (6823, '2025/09/29', '789');
INSERT INTO public.numbers3_draws VALUES (6824, '2025/09/30', '194');
INSERT INTO public.numbers3_draws VALUES (6826, '2025/10/02', '936');
INSERT INTO public.numbers3_draws VALUES (6827, '2025/10/03', '279');
INSERT INTO public.numbers3_draws VALUES (6828, '2025/10/06', '523');
INSERT INTO public.numbers3_draws VALUES (6829, '2025/10/07', '654');
INSERT INTO public.numbers3_draws VALUES (6830, '2025/10/08', '404');
INSERT INTO public.numbers3_draws VALUES (6831, '2025/10/09', '636');
INSERT INTO public.numbers3_draws VALUES (6832, '2025/10/10', '708');
INSERT INTO public.numbers3_draws VALUES (6833, '2025/10/13', '278');
INSERT INTO public.numbers3_draws VALUES (6834, '2025/10/14', '404');
INSERT INTO public.numbers3_draws VALUES (6835, '2025/10/15', '374');
INSERT INTO public.numbers3_draws VALUES (6836, '2025/10/16', '157');
INSERT INTO public.numbers3_draws VALUES (6837, '2025/10/17', '729');


--
-- Data for Name: numbers3_ensemble_predictions; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers3_ensemble_predictions VALUES (1, '2025-10-18 05:44:49.009', 6838, '2025-10-18T05:44:48.979956+00:00', 5, '{"frequency_weight": 0.3, "position_weight": 0.3, "pattern_weight": 0.2, "recent_weight": 0.2}', 10, '[{"number": "123", "score": 0.95}, {"number": "456", "score": 0.92}, {"number": "789", "score": 0.88}, {"number": "012", "score": 0.85}, {"number": "345", "score": 0.82}, {"number": "678", "score": 0.79}, {"number": "901", "score": 0.76}, {"number": "234", "score": 0.73}, {"number": "567", "score": 0.7}, {"number": "890", "score": 0.67}]', '{"frequency_model": ["123", "456", "789", "012", "345"], "position_model": ["456", "789", "012", "345", "678"], "pattern_model": ["123", "012", "345", "678", "901"], "recent_model": ["789", "345", "678", "901", "234"]}', 6838, '123', 'exact', 3, '結果更新: 123 (的中: 3/3桁), 最良予測: 123');


--
-- Data for Name: numbers3_model_events; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers3_model_events VALUES (1, '2025-10-18T05:44:49.062417+00:00', '123', '["123", "456", "789", "012", "345"]', 1, '123', 3, 'テスト用の学習イベント');


--
-- Data for Name: numbers3_prediction_candidates; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers3_prediction_candidates VALUES (1, 1, 1, '123', 0.95, '["frequency_model", "pattern_model"]', '2025-10-18 05:44:49.014');
INSERT INTO public.numbers3_prediction_candidates VALUES (2, 1, 2, '456', 0.92, '["frequency_model", "position_model"]', '2025-10-18 05:44:49.016');
INSERT INTO public.numbers3_prediction_candidates VALUES (3, 1, 3, '789', 0.88, '["frequency_model", "position_model", "recent_model"]', '2025-10-18 05:44:49.017');
INSERT INTO public.numbers3_prediction_candidates VALUES (4, 1, 4, '012', 0.85, '["frequency_model", "position_model", "pattern_model"]', '2025-10-18 05:44:49.018');
INSERT INTO public.numbers3_prediction_candidates VALUES (5, 1, 5, '345', 0.82, '["frequency_model", "position_model", "pattern_model", "recent_model"]', '2025-10-18 05:44:49.02');
INSERT INTO public.numbers3_prediction_candidates VALUES (6, 1, 6, '678', 0.79, '["position_model", "pattern_model", "recent_model"]', '2025-10-18 05:44:49.021');
INSERT INTO public.numbers3_prediction_candidates VALUES (7, 1, 7, '901', 0.76, '["pattern_model", "recent_model"]', '2025-10-18 05:44:49.022');
INSERT INTO public.numbers3_prediction_candidates VALUES (8, 1, 8, '234', 0.73, '["recent_model"]', '2025-10-18 05:44:49.023');
INSERT INTO public.numbers3_prediction_candidates VALUES (9, 1, 9, '567', 0.7, '[]', '2025-10-18 05:44:49.024');
INSERT INTO public.numbers3_prediction_candidates VALUES (10, 1, 10, '890', 0.67, '[]', '2025-10-18 05:44:49.027');


--
-- Data for Name: numbers3_predictions_log; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers3_predictions_log VALUES (1, '2025-10-18T05:44:49.027371+00:00', 'ensemble_prediction', '予測1位', '123', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (2, '2025-10-18T05:44:49.029381+00:00', 'ensemble_prediction', '予測2位', '456', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (3, '2025-10-18T05:44:49.031732+00:00', 'ensemble_prediction', '予測3位', '789', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (4, '2025-10-18T05:44:49.033352+00:00', 'ensemble_prediction', '予測4位', '012', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (5, '2025-10-18T05:44:49.035793+00:00', 'ensemble_prediction', '予測5位', '345', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (6, '2025-10-18T05:44:49.037203+00:00', 'ensemble_prediction', '予測6位', '678', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (7, '2025-10-18T05:44:49.038725+00:00', 'ensemble_prediction', '予測7位', '901', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (8, '2025-10-18T05:44:49.040235+00:00', 'ensemble_prediction', '予測8位', '234', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (9, '2025-10-18T05:44:49.041757+00:00', 'ensemble_prediction', '予測9位', '567', 6838);
INSERT INTO public.numbers3_predictions_log VALUES (10, '2025-10-18T05:44:49.043391+00:00', 'ensemble_prediction', '予測10位', '890', 6838);


--
-- Data for Name: numbers4_draws; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers4_draws VALUES (6633, '2025/01/06', '0685');
INSERT INTO public.numbers4_draws VALUES (6634, '2025/01/07', '3754');
INSERT INTO public.numbers4_draws VALUES (6635, '2025/01/08', '1786');
INSERT INTO public.numbers4_draws VALUES (6636, '2025/01/09', '5802');
INSERT INTO public.numbers4_draws VALUES (6637, '2025/01/10', '1599');
INSERT INTO public.numbers4_draws VALUES (6638, '2025/01/13', '8583');
INSERT INTO public.numbers4_draws VALUES (6639, '2025/01/14', '0135');
INSERT INTO public.numbers4_draws VALUES (6640, '2025/01/15', '1366');
INSERT INTO public.numbers4_draws VALUES (6641, '2025/01/16', '2324');
INSERT INTO public.numbers4_draws VALUES (6642, '2025/01/17', '9774');
INSERT INTO public.numbers4_draws VALUES (6643, '2025/01/20', '4409');
INSERT INTO public.numbers4_draws VALUES (6644, '2025/01/21', '8259');
INSERT INTO public.numbers4_draws VALUES (6645, '2025/01/22', '6385');
INSERT INTO public.numbers4_draws VALUES (6646, '2025/01/23', '5420');
INSERT INTO public.numbers4_draws VALUES (6647, '2025/01/24', '2315');
INSERT INTO public.numbers4_draws VALUES (6648, '2025/01/27', '7240');
INSERT INTO public.numbers4_draws VALUES (6649, '2025/01/28', '0893');
INSERT INTO public.numbers4_draws VALUES (6650, '2025/01/29', '9590');
INSERT INTO public.numbers4_draws VALUES (6651, '2025/01/30', '5400');
INSERT INTO public.numbers4_draws VALUES (6652, '2025/01/31', '1596');
INSERT INTO public.numbers4_draws VALUES (6653, '2025/02/03', '0235');
INSERT INTO public.numbers4_draws VALUES (6654, '2025/02/04', '4827');
INSERT INTO public.numbers4_draws VALUES (6655, '2025/02/05', '2317');
INSERT INTO public.numbers4_draws VALUES (6656, '2025/02/06', '0853');
INSERT INTO public.numbers4_draws VALUES (6657, '2025/02/07', '3881');
INSERT INTO public.numbers4_draws VALUES (6658, '2025/02/10', '0859');
INSERT INTO public.numbers4_draws VALUES (6659, '2025/02/11', '8942');
INSERT INTO public.numbers4_draws VALUES (6660, '2025/02/12', '3343');
INSERT INTO public.numbers4_draws VALUES (6661, '2025/02/13', '1946');
INSERT INTO public.numbers4_draws VALUES (6662, '2025/02/14', '3273');
INSERT INTO public.numbers4_draws VALUES (6663, '2025/02/17', '6744');
INSERT INTO public.numbers4_draws VALUES (6664, '2025/02/18', '0385');
INSERT INTO public.numbers4_draws VALUES (6665, '2025/02/19', '9265');
INSERT INTO public.numbers4_draws VALUES (6666, '2025/02/20', '1890');
INSERT INTO public.numbers4_draws VALUES (6667, '2025/02/21', '6398');
INSERT INTO public.numbers4_draws VALUES (6668, '2025/02/24', '3026');
INSERT INTO public.numbers4_draws VALUES (6669, '2025/02/25', '9378');
INSERT INTO public.numbers4_draws VALUES (6670, '2025/02/26', '0664');
INSERT INTO public.numbers4_draws VALUES (6671, '2025/02/27', '3839');
INSERT INTO public.numbers4_draws VALUES (6672, '2025/02/28', '4968');
INSERT INTO public.numbers4_draws VALUES (6673, '2025/03/03', '1170');
INSERT INTO public.numbers4_draws VALUES (6674, '2025/03/04', '6318');
INSERT INTO public.numbers4_draws VALUES (6675, '2025/03/05', '8194');
INSERT INTO public.numbers4_draws VALUES (6676, '2025/03/06', '1781');
INSERT INTO public.numbers4_draws VALUES (6677, '2025/03/07', '0948');
INSERT INTO public.numbers4_draws VALUES (6678, '2025/03/10', '8256');
INSERT INTO public.numbers4_draws VALUES (6679, '2025/03/11', '8261');
INSERT INTO public.numbers4_draws VALUES (6680, '2025/03/12', '9200');
INSERT INTO public.numbers4_draws VALUES (6681, '2025/03/13', '0384');
INSERT INTO public.numbers4_draws VALUES (6682, '2025/03/14', '2853');
INSERT INTO public.numbers4_draws VALUES (6683, '2025/03/17', '7006');
INSERT INTO public.numbers4_draws VALUES (6684, '2025/03/18', '9843');
INSERT INTO public.numbers4_draws VALUES (6685, '2025/03/19', '1087');
INSERT INTO public.numbers4_draws VALUES (6686, '2025/03/20', '8555');
INSERT INTO public.numbers4_draws VALUES (6687, '2025/03/21', '1431');
INSERT INTO public.numbers4_draws VALUES (6688, '2025/03/24', '0488');
INSERT INTO public.numbers4_draws VALUES (6689, '2025/03/25', '2191');
INSERT INTO public.numbers4_draws VALUES (6690, '2025/03/26', '8397');
INSERT INTO public.numbers4_draws VALUES (6691, '2025/03/27', '0745');
INSERT INTO public.numbers4_draws VALUES (6692, '2025/03/28', '6185');
INSERT INTO public.numbers4_draws VALUES (6693, '2025/03/31', '8221');
INSERT INTO public.numbers4_draws VALUES (6694, '2025/04/01', '3671');
INSERT INTO public.numbers4_draws VALUES (6695, '2025/04/02', '1695');
INSERT INTO public.numbers4_draws VALUES (6696, '2025/04/03', '7892');
INSERT INTO public.numbers4_draws VALUES (6697, '2025/04/04', '9721');
INSERT INTO public.numbers4_draws VALUES (6698, '2025/04/07', '2078');
INSERT INTO public.numbers4_draws VALUES (6699, '2025/04/08', '4417');
INSERT INTO public.numbers4_draws VALUES (6700, '2025/04/09', '4013');
INSERT INTO public.numbers4_draws VALUES (6701, '2025/04/10', '7856');
INSERT INTO public.numbers4_draws VALUES (6702, '2025/04/11', '7011');
INSERT INTO public.numbers4_draws VALUES (6703, '2025/04/14', '1820');
INSERT INTO public.numbers4_draws VALUES (6704, '2025/04/15', '2166');
INSERT INTO public.numbers4_draws VALUES (6705, '2025/04/16', '7555');
INSERT INTO public.numbers4_draws VALUES (6706, '2025/04/17', '8842');
INSERT INTO public.numbers4_draws VALUES (6707, '2025/04/18', '4811');
INSERT INTO public.numbers4_draws VALUES (6708, '2025/04/21', '7834');
INSERT INTO public.numbers4_draws VALUES (6709, '2025/04/22', '6697');
INSERT INTO public.numbers4_draws VALUES (6710, '2025/04/23', '7059');
INSERT INTO public.numbers4_draws VALUES (6711, '2025/04/24', '9686');
INSERT INTO public.numbers4_draws VALUES (6712, '2025/04/25', '4071');
INSERT INTO public.numbers4_draws VALUES (6713, '2025/04/28', '1670');
INSERT INTO public.numbers4_draws VALUES (6714, '2025/04/29', '3449');
INSERT INTO public.numbers4_draws VALUES (6715, '2025/04/30', '5323');
INSERT INTO public.numbers4_draws VALUES (6716, '2025/05/01', '8968');
INSERT INTO public.numbers4_draws VALUES (6717, '2025/05/02', '2948');
INSERT INTO public.numbers4_draws VALUES (6718, '2025/05/05', '8391');
INSERT INTO public.numbers4_draws VALUES (6719, '2025/05/06', '0081');
INSERT INTO public.numbers4_draws VALUES (6720, '2025/05/07', '1952');
INSERT INTO public.numbers4_draws VALUES (6721, '2025/05/08', '8156');
INSERT INTO public.numbers4_draws VALUES (6722, '2025/05/09', '1883');
INSERT INTO public.numbers4_draws VALUES (6723, '2025/05/12', '8892');
INSERT INTO public.numbers4_draws VALUES (6724, '2025/05/13', '9565');
INSERT INTO public.numbers4_draws VALUES (6725, '2025/05/14', '1898');
INSERT INTO public.numbers4_draws VALUES (6726, '2025/05/15', '4368');
INSERT INTO public.numbers4_draws VALUES (6727, '2025/05/16', '4116');
INSERT INTO public.numbers4_draws VALUES (6728, '2025/05/19', '9601');
INSERT INTO public.numbers4_draws VALUES (6729, '2025/05/20', '6418');
INSERT INTO public.numbers4_draws VALUES (6730, '2025/05/21', '2762');
INSERT INTO public.numbers4_draws VALUES (6731, '2025/05/22', '9899');
INSERT INTO public.numbers4_draws VALUES (6732, '2025/05/23', '2718');
INSERT INTO public.numbers4_draws VALUES (6733, '2025/05/26', '9115');
INSERT INTO public.numbers4_draws VALUES (6734, '2025/05/27', '3697');
INSERT INTO public.numbers4_draws VALUES (6735, '2025/05/28', '7357');
INSERT INTO public.numbers4_draws VALUES (6736, '2025/05/29', '6779');
INSERT INTO public.numbers4_draws VALUES (6737, '2025/05/30', '7141');
INSERT INTO public.numbers4_draws VALUES (6738, '2025/06/02', '2839');
INSERT INTO public.numbers4_draws VALUES (6739, '2025/06/03', '2370');
INSERT INTO public.numbers4_draws VALUES (6740, '2025/06/04', '5944');
INSERT INTO public.numbers4_draws VALUES (6741, '2025/06/05', '9318');
INSERT INTO public.numbers4_draws VALUES (6742, '2025/06/06', '6563');
INSERT INTO public.numbers4_draws VALUES (6743, '2025/06/09', '5084');
INSERT INTO public.numbers4_draws VALUES (6744, '2025/06/10', '3142');
INSERT INTO public.numbers4_draws VALUES (6745, '2025/06/11', '3176');
INSERT INTO public.numbers4_draws VALUES (6746, '2025/06/12', '7666');
INSERT INTO public.numbers4_draws VALUES (6747, '2025/06/13', '2482');
INSERT INTO public.numbers4_draws VALUES (6748, '2025/06/16', '6326');
INSERT INTO public.numbers4_draws VALUES (6749, '2025/06/17', '0975');
INSERT INTO public.numbers4_draws VALUES (6750, '2025/06/18', '7592');
INSERT INTO public.numbers4_draws VALUES (6751, '2025/06/19', '5354');
INSERT INTO public.numbers4_draws VALUES (6752, '2025/06/20', '7102');
INSERT INTO public.numbers4_draws VALUES (6753, '2025/06/23', '4804');
INSERT INTO public.numbers4_draws VALUES (6754, '2025/06/24', '1351');
INSERT INTO public.numbers4_draws VALUES (6755, '2025/06/25', '8174');
INSERT INTO public.numbers4_draws VALUES (6756, '2025/06/26', '8622');
INSERT INTO public.numbers4_draws VALUES (6757, '2025/06/27', '2940');
INSERT INTO public.numbers4_draws VALUES (6758, '2025/06/30', '6757');
INSERT INTO public.numbers4_draws VALUES (6759, '2025/07/01', '5261');
INSERT INTO public.numbers4_draws VALUES (6760, '2025/07/02', '3099');
INSERT INTO public.numbers4_draws VALUES (6761, '2025/07/03', '1479');
INSERT INTO public.numbers4_draws VALUES (6762, '2025/07/04', '2452');
INSERT INTO public.numbers4_draws VALUES (6763, '2025/07/07', '9181');
INSERT INTO public.numbers4_draws VALUES (6764, '2025/07/08', '2982');
INSERT INTO public.numbers4_draws VALUES (6765, '2025/07/09', '5358');
INSERT INTO public.numbers4_draws VALUES (6766, '2025/07/10', '4790');
INSERT INTO public.numbers4_draws VALUES (6767, '2025/07/11', '0172');
INSERT INTO public.numbers4_draws VALUES (6768, '2025/07/14', '5295');
INSERT INTO public.numbers4_draws VALUES (6769, '2025/07/15', '5552');
INSERT INTO public.numbers4_draws VALUES (6770, '2025/07/16', '2037');
INSERT INTO public.numbers4_draws VALUES (6771, '2025/07/17', '2337');
INSERT INTO public.numbers4_draws VALUES (6772, '2025/07/18', '2460');
INSERT INTO public.numbers4_draws VALUES (6773, '2025/07/21', '7780');
INSERT INTO public.numbers4_draws VALUES (6774, '2025/07/22', '8714');
INSERT INTO public.numbers4_draws VALUES (6775, '2025/07/23', '5493');
INSERT INTO public.numbers4_draws VALUES (6776, '2025/07/24', '7924');
INSERT INTO public.numbers4_draws VALUES (6777, '2025/07/25', '5454');
INSERT INTO public.numbers4_draws VALUES (6778, '2025/07/28', '6710');
INSERT INTO public.numbers4_draws VALUES (6779, '2025/07/29', '1592');
INSERT INTO public.numbers4_draws VALUES (6780, '2025/07/30', '3175');
INSERT INTO public.numbers4_draws VALUES (6781, '2025/07/31', '0536');
INSERT INTO public.numbers4_draws VALUES (6782, '2025/08/01', '3497');
INSERT INTO public.numbers4_draws VALUES (6783, '2025/08/04', '3080');
INSERT INTO public.numbers4_draws VALUES (6784, '2025/08/05', '1027');
INSERT INTO public.numbers4_draws VALUES (6785, '2025/08/06', '4876');
INSERT INTO public.numbers4_draws VALUES (6786, '2025/08/07', '5835');
INSERT INTO public.numbers4_draws VALUES (6787, '2025/08/08', '1365');
INSERT INTO public.numbers4_draws VALUES (6788, '2025/08/11', '6014');
INSERT INTO public.numbers4_draws VALUES (6789, '2025/08/12', '2458');
INSERT INTO public.numbers4_draws VALUES (6790, '2025/08/13', '5541');
INSERT INTO public.numbers4_draws VALUES (6791, '2025/08/14', '6362');
INSERT INTO public.numbers4_draws VALUES (6792, '2025/08/15', '5140');
INSERT INTO public.numbers4_draws VALUES (6793, '2025/08/18', '9959');
INSERT INTO public.numbers4_draws VALUES (6794, '2025/08/19', '9288');
INSERT INTO public.numbers4_draws VALUES (6795, '2025/08/20', '8749');
INSERT INTO public.numbers4_draws VALUES (6796, '2025/08/21', '5806');
INSERT INTO public.numbers4_draws VALUES (6797, '2025/08/22', '9660');
INSERT INTO public.numbers4_draws VALUES (6798, '2025/08/25', '9463');
INSERT INTO public.numbers4_draws VALUES (6799, '2025/08/26', '1624');
INSERT INTO public.numbers4_draws VALUES (6800, '2025/08/27', '6694');
INSERT INTO public.numbers4_draws VALUES (6801, '2025/08/28', '0774');
INSERT INTO public.numbers4_draws VALUES (6802, '2025/08/29', '1929');
INSERT INTO public.numbers4_draws VALUES (6803, '2025/09/01', '0549');
INSERT INTO public.numbers4_draws VALUES (6804, '2025/09/02', '0538');
INSERT INTO public.numbers4_draws VALUES (6805, '2025/09/03', '4598');
INSERT INTO public.numbers4_draws VALUES (6806, '2025/09/04', '3376');
INSERT INTO public.numbers4_draws VALUES (6807, '2025/09/05', '1871');
INSERT INTO public.numbers4_draws VALUES (6808, '2025/09/08', '2841');
INSERT INTO public.numbers4_draws VALUES (6809, '2025/09/09', '5260');
INSERT INTO public.numbers4_draws VALUES (6810, '2025/09/10', '2679');
INSERT INTO public.numbers4_draws VALUES (6811, '2025/09/11', '7961');
INSERT INTO public.numbers4_draws VALUES (6812, '2025/09/12', '8991');
INSERT INTO public.numbers4_draws VALUES (6813, '2025/09/15', '6867');
INSERT INTO public.numbers4_draws VALUES (6814, '2025/09/16', '1314');
INSERT INTO public.numbers4_draws VALUES (6815, '2025/09/17', '7604');
INSERT INTO public.numbers4_draws VALUES (6816, '2025/09/18', '6152');
INSERT INTO public.numbers4_draws VALUES (6817, '2025/09/19', '8721');
INSERT INTO public.numbers4_draws VALUES (6818, '2025/09/22', '5808');
INSERT INTO public.numbers4_draws VALUES (6819, '2025/09/23', '4787');
INSERT INTO public.numbers4_draws VALUES (6820, '2025/09/24', '2477');
INSERT INTO public.numbers4_draws VALUES (6821, '2025/09/25', '7728');
INSERT INTO public.numbers4_draws VALUES (6822, '2025/09/26', '1540');
INSERT INTO public.numbers4_draws VALUES (6823, '2025/09/29', '0012');
INSERT INTO public.numbers4_draws VALUES (6824, '2025/09/30', '7765');
INSERT INTO public.numbers4_draws VALUES (6825, '2025/10/01', '5280');
INSERT INTO public.numbers4_draws VALUES (6826, '2025/10/02', '1916');
INSERT INTO public.numbers4_draws VALUES (6827, '2025/10/03', '2964');
INSERT INTO public.numbers4_draws VALUES (6828, '2025/10/06', '0933');
INSERT INTO public.numbers4_draws VALUES (6829, '2025/10/07', '7717');
INSERT INTO public.numbers4_draws VALUES (6830, '2025/10/08', '0220');
INSERT INTO public.numbers4_draws VALUES (6831, '2025/10/09', '6352');
INSERT INTO public.numbers4_draws VALUES (6832, '2025/10/10', '3148');
INSERT INTO public.numbers4_draws VALUES (6833, '2025/10/13', '6896');
INSERT INTO public.numbers4_draws VALUES (6834, '2025/10/14', '4706');
INSERT INTO public.numbers4_draws VALUES (6835, '2025/10/15', '1350');
INSERT INTO public.numbers4_draws VALUES (6836, '2025/10/16', '4325');
INSERT INTO public.numbers4_draws VALUES (6837, '2025/10/17', '5441');


--
-- Data for Name: numbers4_ensemble_predictions; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers4_ensemble_predictions VALUES (1, '2025-10-18 05:36:59.584', 6833, '2025-10-17T14:53:41.292259+00:00', 10, '{"frequency_weight": 0.3, "position_weight": 0.3, "pattern_weight": 0.2, "recent_weight": 0.2}', 4, '[{"number": "9660", "score": 0.85}, {"number": "9760", "score": 0.82}, {"number": "9604", "score": 0.78}, {"number": "5871", "score": 0.75}]', '{"frequency_model": ["9660", "9760"], "position_model": ["9604", "5871"], "pattern_model": ["9660", "9604"], "recent_model": ["9760", "5871"]}', NULL, NULL, NULL, NULL, '復元されたサンプル予測データ');
INSERT INTO public.numbers4_ensemble_predictions VALUES (2, '2025-10-18 08:08:10.453', 6838, '2025-10-17T14:53:41.292259+00:00', 10, '{"basic_stats": 1.2, "advanced_heuristics": 1.5, "ml_model_new": 1.0, "exploratory": 0.9}', 30, '[{"rank": 1, "number": "5414", "score": 1.5}, {"rank": 2, "number": "7176", "score": 1.5}, {"rank": 3, "number": "3541", "score": 1.5}, {"rank": 4, "number": "4545", "score": 1.5}, {"rank": 5, "number": "4176", "score": 1.5}, {"rank": 6, "number": "2890", "score": 1.2}, {"rank": 7, "number": "0457", "score": 1.2}, {"rank": 8, "number": "4877", "score": 1.2}, {"rank": 9, "number": "5741", "score": 1.2}, {"rank": 10, "number": "2950", "score": 1.2}, {"rank": 11, "number": "5940", "score": 1.0}, {"rank": 12, "number": "1485", "score": 1.0}, {"rank": 13, "number": "6354", "score": 1.0}, {"rank": 14, "number": "5483", "score": 1.0}, {"rank": 15, "number": "9540", "score": 1.0}, {"rank": 16, "number": "5960", "score": 1.0}, {"rank": 17, "number": "5409", "score": 1.0}, {"rank": 18, "number": "1890", "score": 1.0}, {"rank": 19, "number": "4831", "score": 1.0}, {"rank": 20, "number": "4871", "score": 1.0}]', '{"basic_stats": {"count": 5, "predictions": ["2890", "2950", "5741", "4877", "0457"]}, "advanced_heuristics": {"count": 5, "predictions": ["5414", "7176", "4176", "4545", "3541"]}, "ml_model_new": {"count": 15, "predictions": ["5940", "1485", "6354", "5483", "9540", "5960", "5409", "1890", "4831", "4871"]}, "exploratory": {"count": 5, "predictions": ["8778", "3024", "8788", "6897", "8879"]}}', NULL, NULL, NULL, NULL, 'Ensemble prediction with improved time-weighted models');


--
-- Data for Name: numbers4_model_events; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers4_model_events VALUES (1, '2025-10-17T14:53:41.292259+00:00', '0000', '[]', 0, NULL, 0, 'Model state restored from numbers4/model_state.json');


--
-- Data for Name: numbers4_prediction_candidates; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers4_prediction_candidates VALUES (1, 1, 1, '9660', 0.85, '["ensemble_model"]', '2025-10-18 05:36:59.618');
INSERT INTO public.numbers4_prediction_candidates VALUES (2, 1, 2, '9760', 0.82, '["ensemble_model"]', '2025-10-18 05:36:59.622');
INSERT INTO public.numbers4_prediction_candidates VALUES (3, 1, 3, '9604', 0.78, '["ensemble_model"]', '2025-10-18 05:36:59.623');
INSERT INTO public.numbers4_prediction_candidates VALUES (4, 1, 4, '5871', 0.75, '["ensemble_model"]', '2025-10-18 05:36:59.624');
INSERT INTO public.numbers4_prediction_candidates VALUES (5, 2, 1, '5414', 1.5, '["advanced_heuristics"]', '2025-10-18 08:08:10.468');
INSERT INTO public.numbers4_prediction_candidates VALUES (6, 2, 2, '7176', 1.5, '["advanced_heuristics"]', '2025-10-18 08:08:10.481');
INSERT INTO public.numbers4_prediction_candidates VALUES (7, 2, 3, '3541', 1.5, '["advanced_heuristics"]', '2025-10-18 08:08:10.484');
INSERT INTO public.numbers4_prediction_candidates VALUES (8, 2, 4, '4545', 1.5, '["advanced_heuristics"]', '2025-10-18 08:08:10.485');
INSERT INTO public.numbers4_prediction_candidates VALUES (9, 2, 5, '4176', 1.5, '["advanced_heuristics"]', '2025-10-18 08:08:10.486');
INSERT INTO public.numbers4_prediction_candidates VALUES (10, 2, 6, '2890', 1.2, '["basic_stats"]', '2025-10-18 08:08:10.488');
INSERT INTO public.numbers4_prediction_candidates VALUES (11, 2, 7, '0457', 1.2, '["basic_stats"]', '2025-10-18 08:08:10.49');
INSERT INTO public.numbers4_prediction_candidates VALUES (12, 2, 8, '4877', 1.2, '["basic_stats"]', '2025-10-18 08:08:10.491');
INSERT INTO public.numbers4_prediction_candidates VALUES (13, 2, 9, '5741', 1.2, '["basic_stats"]', '2025-10-18 08:08:10.491');
INSERT INTO public.numbers4_prediction_candidates VALUES (14, 2, 10, '2950', 1.2, '["basic_stats"]', '2025-10-18 08:08:10.492');
INSERT INTO public.numbers4_prediction_candidates VALUES (15, 2, 11, '5940', 1, '["ml_model_new"]', '2025-10-18 08:08:10.493');
INSERT INTO public.numbers4_prediction_candidates VALUES (16, 2, 12, '1485', 1, '["ml_model_new"]', '2025-10-18 08:08:10.495');
INSERT INTO public.numbers4_prediction_candidates VALUES (17, 2, 13, '6354', 1, '["ml_model_new"]', '2025-10-18 08:08:10.496');
INSERT INTO public.numbers4_prediction_candidates VALUES (18, 2, 14, '5483', 1, '["ml_model_new"]', '2025-10-18 08:08:10.497');
INSERT INTO public.numbers4_prediction_candidates VALUES (19, 2, 15, '9540', 1, '["ml_model_new"]', '2025-10-18 08:08:10.498');
INSERT INTO public.numbers4_prediction_candidates VALUES (20, 2, 16, '5960', 1, '["ml_model_new"]', '2025-10-18 08:08:10.5');
INSERT INTO public.numbers4_prediction_candidates VALUES (21, 2, 17, '5409', 1, '["ml_model_new"]', '2025-10-18 08:08:10.501');
INSERT INTO public.numbers4_prediction_candidates VALUES (22, 2, 18, '1890', 1, '["ml_model_new"]', '2025-10-18 08:08:10.502');
INSERT INTO public.numbers4_prediction_candidates VALUES (23, 2, 19, '4831', 1, '["ml_model_new"]', '2025-10-18 08:08:10.504');
INSERT INTO public.numbers4_prediction_candidates VALUES (24, 2, 20, '4871', 1, '["ml_model_new"]', '2025-10-18 08:08:10.505');
INSERT INTO public.numbers4_prediction_candidates VALUES (25, 2, 21, '5920', 1, '["ml_model_new"]', '2025-10-18 08:08:10.505');
INSERT INTO public.numbers4_prediction_candidates VALUES (26, 2, 22, '9631', 1, '["ml_model_new"]', '2025-10-18 08:08:10.507');
INSERT INTO public.numbers4_prediction_candidates VALUES (27, 2, 23, '5249', 1, '["ml_model_new"]', '2025-10-18 08:08:10.508');
INSERT INTO public.numbers4_prediction_candidates VALUES (28, 2, 24, '5463', 1, '["ml_model_new"]', '2025-10-18 08:08:10.509');
INSERT INTO public.numbers4_prediction_candidates VALUES (29, 2, 25, '6381', 1, '["ml_model_new"]', '2025-10-18 08:08:10.51');
INSERT INTO public.numbers4_prediction_candidates VALUES (30, 2, 26, '8778', 0.9, '["exploratory"]', '2025-10-18 08:08:10.511');
INSERT INTO public.numbers4_prediction_candidates VALUES (31, 2, 27, '3024', 0.9, '["exploratory"]', '2025-10-18 08:08:10.512');
INSERT INTO public.numbers4_prediction_candidates VALUES (32, 2, 28, '8788', 0.9, '["exploratory"]', '2025-10-18 08:08:10.514');
INSERT INTO public.numbers4_prediction_candidates VALUES (33, 2, 29, '6897', 0.9, '["exploratory"]', '2025-10-18 08:08:10.515');
INSERT INTO public.numbers4_prediction_candidates VALUES (34, 2, 30, '8879', 0.9, '["exploratory"]', '2025-10-18 08:08:10.515');


--
-- Data for Name: numbers4_predictions_log; Type: TABLE DATA; Schema: public; Owner: user
--

INSERT INTO public.numbers4_predictions_log VALUES (1, '2025-10-18T05:36:59.550677+00:00', 'prediction_result.md', '予測1位', '2025', 6833);
INSERT INTO public.numbers4_predictions_log VALUES (2, '2025-10-18T05:36:59.550677+00:00', 'prediction_result.md', '予測2位', '2025', 6833);
INSERT INTO public.numbers4_predictions_log VALUES (3, '2025-10-18T05:36:59.550677+00:00', 'prediction_result.md', '予測3位', '6185', 6833);
INSERT INTO public.numbers4_predictions_log VALUES (4, '2025-10-18T05:36:59.550677+00:00', 'prediction_result.md', '予測4位', '6960', 6833);
INSERT INTO public.numbers4_predictions_log VALUES (5, '2025-10-18T05:36:59.550677+00:00', 'prediction_result.md', '予測5位', '2039', 6833);
INSERT INTO public.numbers4_predictions_log VALUES (6, '2025-10-18T05:36:59.550677+00:00', 'prediction_result.md', '予測6位', '6183', 6833);
INSERT INTO public.numbers4_predictions_log VALUES (7, '2025-10-18T05:36:59.550677+00:00', 'advanced_prediction_result.md', '高度予測1位', '9660', NULL);
INSERT INTO public.numbers4_predictions_log VALUES (8, '2025-10-18T05:36:59.550677+00:00', 'advanced_prediction_result.md', '高度予測2位', '9760', NULL);
INSERT INTO public.numbers4_predictions_log VALUES (9, '2025-10-18T05:36:59.550677+00:00', 'advanced_prediction_result.md', '高度予測3位', '9604', NULL);
INSERT INTO public.numbers4_predictions_log VALUES (10, '2025-10-18T05:36:59.550677+00:00', 'advanced_prediction_result.md', '高度予測4位', '5871', NULL);


--
-- Name: loto6_ensemble_predictions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.loto6_ensemble_predictions_id_seq', 2, true);


--
-- Name: loto6_model_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.loto6_model_events_id_seq', 2, true);


--
-- Name: loto6_prediction_candidates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.loto6_prediction_candidates_id_seq', 20, true);


--
-- Name: loto6_predictions_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.loto6_predictions_log_id_seq', 20, true);


--
-- Name: numbers3_ensemble_predictions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers3_ensemble_predictions_id_seq', 1, true);


--
-- Name: numbers3_model_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers3_model_events_id_seq', 1, true);


--
-- Name: numbers3_prediction_candidates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers3_prediction_candidates_id_seq', 10, true);


--
-- Name: numbers3_predictions_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers3_predictions_log_id_seq', 10, true);


--
-- Name: numbers4_ensemble_predictions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers4_ensemble_predictions_id_seq', 2, true);


--
-- Name: numbers4_model_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers4_model_events_id_seq', 1, true);


--
-- Name: numbers4_prediction_candidates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers4_prediction_candidates_id_seq', 34, true);


--
-- Name: numbers4_predictions_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.numbers4_predictions_log_id_seq', 10, true);


--
-- PostgreSQL database dump complete
--

\unrestrict GDrkXE2RaVNkmYoSYwWRBf87nLtmqzcpbLVe7UMInD09cPvEV5ce5oBmML5oPDo

