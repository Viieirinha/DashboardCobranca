with fat_anterior as (
	select 
	--9942500
		f.financial_renegotiation_id as id,
		min(f.expiration_date) as vencimento_mais_antigo
	from financial_renegotiation_titles f
	group by f.financial_renegotiation_id
)
SELECT
    c.id AS "CONTRATO",
    p."name" AS "CLIENTE",
    c.v_stage AS "ESTÁGIO",
    c.v_status AS "SITUAÇÃO",
    vu."name" AS "OPERADOR",
    frt.title AS "FAT",
--    rt.financial_renegotiation_id,
--    fa.vencimento_mais_antigo,
    fn.title AS "NATUREZA FINANCE",
    frt.complement AS "COMPLEMENTO",
    frt.entry_date AS "DATA_EMISSAO",
    pf.title AS "PAGAMENTO",
    case
    	when p.cell_phone_1 is null then p.phone
    	else p.cell_phone_1
    end as "CONTATO",
    case
    	when t.total_amount is null then frt.v_final_amount
    	else t.total_amount
    end as "VALOR_TOTAL",
    frt.renegotiated as "RENEGOCIADO",
    frt.parcel as "PARCELA",
    t.receipt_date AS Date_last_paid,
    t.total_amount as "Val_last_paid",
    CASE
        WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 1 AND 9 THEN 'ABAIXO DE 10 DIAS'
    	WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 10 AND 29 THEN '10 A 29 DIAS'
    	WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 30 AND 45 THEN '30 A 45 DIAS'
    	WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 46 AND 60 THEN '46 A 60 DIAS'
    	WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 61 AND 75 THEN '61 A 75 DIAS'
    	WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 76 AND 90 THEN '76 A 90 DIAS'
    	WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 91 AND 180 THEN '91 A 180 DIAS'
    	WHEN frt.entry_date - fa.vencimento_mais_antigo BETWEEN 181 AND 360 THEN '181 A 360 DIAS'
   	 	WHEN frt.entry_date - fa.vencimento_mais_antigo > 360 THEN '(+) 361 DIAS'
    	ELSE 'ABAIXO DE 10 DIAS'
	END AS "FAIXA_DE_ATRASO",
        frt.entry_date - (LAG(frt.expiration_date) OVER (PARTITION BY frt.contract_id ORDER BY frt.expiration_date)) as "DIAS_ATRASO",
    CASE
        WHEN EXISTS (SELECT * FROM erp.financial_receipt_titles t WHERE t.financial_receivable_title_id = frt.id) THEN '0'
        ELSE CURRENT_DATE - frt.expiration_date
    END AS Days_open,  
    CASE
        WHEN t.receipt_date IS NULL THEN 'ABERTO'
        ELSE 'PAGO'
    END AS "STATUS_PAGAMENTO",
    case
    	when frt.complement ilike '%renegociação%' then 'RENEGOCIADO'
	    else 'NÃO RENEGOCIADO'
    end as "RENEGOCIADO",
    CASE
        WHEN frt.expiration_date = frt.original_expiration_date THEN 'NÃO REAGENDADO'
        ELSE 'REAGENDADO'
    END AS "REAGENDAMENTO",
    frt.expiration_date AS "VCTO",
    case
	    when EXISTS (SELECT * FROM erp.financial_receipt_titles t WHERE t.financial_receivable_title_id = frt.id) THEN 'PAGO'
    	WHEN CURRENT_DATE - frt.expiration_date > 0 then 'VENCIDO'
    	--when CURRENT_DATE - frt.expiration_date < 0 then 'A VENCER'
        ELSE 'A VENCER'
    end "STATUS_RECEBIMENTO",
    frt.original_expiration_date,
    case 
    	when t.receipt_date is NULL then frt.expiration_date
    	else t.receipt_date
    end as "FILTRO_1",   
    case 
    	when t.receipt_date is NULL then frt.expiration_date
    	else t.receipt_date
    end as "FILTRO_2"   
FROM financial_receivable_titles frt
INNER JOIN erp.financers_natures fn ON fn.id = frt.financer_nature_id
LEFT JOIN erp.financial_receipt_titles t ON t.financial_receivable_title_id = frt.id
LEFT JOIN erp.v_users vu ON vu.id = frt.created_by
LEFT JOIN payment_forms pf ON t.payment_form_id = pf.id  
left join contracts c on c.id = frt.contract_id
INNER JOIN erp.people p ON p.id = frt.client_id
left join financial_renegotiation_titles rt on rt.financial_receivable_title_id = frt.id
left join fat_anterior fa on fa.id = rt.financial_renegotiation_id
WHERE
    fn.id in (140, 59)	
	and frt.entry_date between '2025-01-01' and '2026-12-31' 
    and not exists (select * from financial_receivable_titles tt
    				where tt.id = frt.id
    				and tt.financer_nature_id != 140
    				and tt.expiration_date = tt.original_expiration_date)
 
    and frt.title ilike 'fat%'
    and frt.id != 9942638
--    and c.id = 43874 
    and vu.id in (996,1066,1032,1072,461,1067,1069,1070,1096,1097,1071,1073,1135, 1167,1185, 1224, 1235, 
    1232, 1233, 1250, 1294, 1293, 1312, 1311, 1316, 1318, 1320, 1319, 1352, 1385, 1376, 1446, 1445, 1449, 
    1455, 1476, 1492, 176, 1357, 1596, 1597, 1697, 1458, 1382, 1748, 1883, 1884, 1538, 1977, 2098, 2148, 2175)
    --(1232,1066,1235,1167,1073,1233,1311,1312,1072,1316,1318,1320,1319)
    order by frt.contract_id
    