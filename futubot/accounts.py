import time

from futu import (RET_OK, KLType, Market, ModifyOrderOp, OpenQuoteContext,
                  OpenSecTradeContext, OrderStatus, OrderType, SecurityFirm,
                  SecurityType, TrdEnv, TrdMarket)


class Accounts:
    def __init__(self,
                 host='127.0.0.1',
                 port=11111,
                 filter_trdmarket=TrdMarket.HK,
                 security_firm=SecurityFirm.FUTUSECURITIES,
                 paper_trading=False,
                 password='******'):
        self.host = host
        self.port = port
        self.filter_trdmarket = filter_trdmarket
        self.security_firm = security_firm
        self.quote_context = self.create_quote_context()
        self.trade_context = self.create_trade_context()
        self.trd_env = TrdEnv.REAL
        self.paper_trading = paper_trading
        self.password = password

        if self.paper_trading:
            self.trd_env = TrdEnv.SIMULATE

    def create_quote_context(self):
        quote_context = OpenQuoteContext(host=self.host, port=self.port)
        return quote_context

    def create_trade_context(self):
        trade_context = OpenSecTradeContext(
            filter_trdmarket=self.filter_trdmarket,
            host=self.host,
            port=self.port,
            security_firm=self.security_firm)
        return trade_context

    def get_market_state(self, code_list):

        if not isinstance(code_list, list):
            raise TypeError(f'Only list type is supported for code_list, '
                            f'but got {type(code_list)}')

        market_state = {}

        ret, data = self.quote_context.get_market_state(code_list=code_list)

        if ret == RET_OK:
            for _, row in data.iterrows():
                code = row['code']

                if code not in market_state:
                    market_state[code] = {}
                market_state[code]['stock_name'] = row['stock_name']
                market_state[code]['market_state'] = row['market_state']

            return market_state

        else:
            print('Error in get_market_state: ', data)

    def get_account_list(self):

        account_list = {}

        ret, data = self.trade_context.get_acc_list()

        if ret == RET_OK:
            for _, row in data.iterrows():
                acc_id = row['acc_id']

                if acc_id not in account_list:
                    account_list[acc_id] = {}

                account_list[acc_id]['trd_env'] = row['trd_env']
                account_list[acc_id]['acc_type'] = row['acc_type']
                account_list[acc_id]['card_num'] = row['card_num']
                account_list[acc_id]['security_firm'] = row['security_firm']
                account_list[acc_id]['sim_acc_type'] = row['sim_acc_type']
                account_list[acc_id]['trdmarket_auth'] = row['trdmarket_auth']

            return account_list
        else:
            print('Error in get_account_list: ', data)

    def get_account_info(self):

        account_info = {}

        ret, data = self.trade_context.accinfo_query(trd_env=self.trd_env)

        if ret == RET_OK:
            account_info['power'] = data['power'][0]
            account_info['max_power_short'] = data['max_power_short'][0]
            account_info['net_cash_power'] = data['net_cash_power'][0]
            account_info['total_assets'] = data['total_assets'][0]
            account_info['cash'] = data['cash'][0]
            account_info['total_market_value'] = data['market_val'][0]
            return account_info
        else:
            print('Error in get_account_info: ', data)

    def get_historical_candles(self,
                               code,
                               start,
                               end,
                               ktype=KLType.K_1M,
                               max_count=1000):

        if not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')

        if not isinstance(start, str):
            raise TypeError(f'Only str type is supported for start, '
                            f'but got {type(start)}')

        if not isinstance(end, str):
            raise TypeError(f'Only str type is supported for end, '
                            f'but got {type(end)}')

        if not isinstance(ktype, str):
            raise TypeError(f'Only str type is supported for ktype, '
                            f'but got {type(ktype)}')

        if not isinstance(max_count, int):
            raise TypeError(f'Only int type is supported for max_count, '
                            f'but got {type(max_count)}')

        ret, data, page_req_key = self.quote_context.request_history_kline(
            code=code, start=start, end=end, ktype=ktype, max_count=max_count)

        if ret == RET_OK:
            return data
        else:
            print('Error in get_historical_candles: ', data)

    def get_positions(self, code=''):

        if code != '' and not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')

        positions_dict = {}

        ret, data = self.trade_context.position_list_query(
            code=code, trd_env=self.trd_env)

        if ret == RET_OK:

            if data.empty:
                return {}

            else:

                for _, row in data.iterrows():

                    code = row['code']
                    if code not in positions_dict:
                        positions_dict[code] = {}

                    positions_dict[code]['code'] = code
                    positions_dict[code]['position_side'] = row[
                        'position_side']
                    positions_dict[code]['stock_name'] = row['stock_name']
                    positions_dict[code]['qty'] = row['qty']
                    positions_dict[code]['cost_price'] = row['cost_price']
                    positions_dict[code]['market_value'] = row['market_val']
                    positions_dict[code]['current_price'] = row[
                        'nominal_price']
                    positions_dict[code]['pnl_ratio'] = row['pl_ratio']
                    positions_dict[code]['pnl_value'] = row['pl_val']

            return positions_dict
        else:
            print('Error in get_positions: ', data)

    def unlock_trade(self, password, is_unlock=True):

        if not isinstance(password, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(password)}')

        if not isinstance(is_unlock, bool):
            raise TypeError(f'Only bool type is supported for is_unlock, '
                            f'but got {type(is_unlock)}')

        ret, data = self.trade_context.unlock_trade(password,
                                                    is_unlock=is_unlock)

        if ret == RET_OK:
            print('Unlock success!')
            return True
        else:
            print('Unlock failed: ', data)
            return False

    def place_order(self, price, qty, code, trd_side, order_type='limit'):

        if not isinstance(price, float):
            raise TypeError(f'Only float type is supported for price, '
                            f'but got {type(price)}')

        if not isinstance(qty, float):
            raise TypeError(f'Only float type is supported for qty, '
                            f'but got {type(qty)}')

        if not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')

        if not isinstance(trd_side, str):
            raise TypeError(f'Only str type is supported for trd_side, '
                            f'but got {type(trd_side)}')

        if not isinstance(order_type, str):
            raise TypeError(f'Only str type is supported for order_type, '
                            f'but got {type(order_type)}')

        if order_type == 'market' and self.paper_trading is True:
            raise ValueError('Paper trading does not support market order')

        if order_type == 'market':
            order_type = OrderType.MARKET
        elif order_type == 'limit':
            order_type = OrderType.NORMAL

        order_info = {}

        if self.unlock_trade(self.password):
            ret, data = self.trade_context.place_order(price=price,
                                                       qty=qty,
                                                       code=code,
                                                       trd_side=trd_side,
                                                       order_type=order_type,
                                                       trd_env=self.trd_env)

            if ret == RET_OK:

                # print(data)
                order_info['trd_side'] = data['trd_side'][0]
                order_info['order_type'] = data['order_type'][0]
                order_info['order_status'] = data['order_status'][0]
                order_info['order_id'] = data['order_id'][0]
                order_info['code'] = data['code'][0]
                order_info['stock_name'] = data['stock_name'][0]
                order_info['qty'] = data['qty'][0]
                order_info['price'] = data['price'][0]
                order_info['create_time'] = data['create_time'][0]
                order_info['updated_time'] = data['updated_time'][0]

                time.sleep(0.02)
                return order_info
            else:
                print('Error in place_order: ', data)
        else:
            print('Unlock failed!')

    def get_lot_size(self,
                     code_list,
                     market=Market.HK,
                     stock_type=SecurityType.STOCK):

        if not isinstance(code_list, list):
            raise TypeError(f'Only list type is supported for code_list, '
                            f'but got {type(code_list)}')

        if not isinstance(market, str):
            raise TypeError(f'Only str type is supported for market, '
                            f'but got {type(market)}')

        if not isinstance(stock_type, str):
            raise TypeError(f'Only str type is supported for stock_type, '
                            f'but got {type(stock_type)}')

        lot_sizes = {}

        ret, data = self.quote_context.get_stock_basicinfo(
            market=market, stock_type=stock_type, code_list=code_list)

        if ret == RET_OK:
            for code in code_list:
                lot_sizes[code] = float(
                    data[data['code'] == code]['lot_size'].item())
            return lot_sizes
        else:
            print('Error in get_lot_size: ', data)

    def check_today_orders(self, code='', status_filter_list=[]):

        if code != '' and not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')

        if status_filter_list != [] and not isinstance(status_filter_list,
                                                       list):
            raise TypeError(
                f'Only str type is supported for status_filter_list, '
                f'but got {type(status_filter_list)}')

        ret, data = self.trade_context.order_list_query(
            code=code,
            status_filter_list=status_filter_list,
            trd_env=self.trd_env)

        if ret == RET_OK:
            if data.shape[0] > 0:  # If the order list is not empty
                data = data[[
                    'order_id', 'code', 'stock_name', 'trd_side', 'order_type',
                    'qty', 'order_status', 'price', 'currency', 'create_time',
                    'updated_time'
                ]]
                return data
            else:
                return None
        else:
            print('Error in check_today_orders: ', data)

    def check_existing_orders(self, code_list):

        if not isinstance(code_list, (list, dict)):
            raise TypeError(
                f'Only list or dict type is supported for code_list, '
                f'but got {type(code_list)}')

        existing_orders = {}

        ret, data = self.trade_context.history_order_list_query(
            trd_env=self.trd_env)

        if ret == RET_OK:
            if data.shape[0] > 0:
                for code in code_list:
                    if data[(data['code'] == code)
                            & (data['order_status'] == OrderStatus.SUBMITTED
                               )].shape[0] > 0:
                        existing_orders[code] = True
                    else:
                        existing_orders[code] = False
            return existing_orders

        else:
            print('Error in check_existing_orders: ', data)

    def get_max_power(self, code, price, order_type=OrderType.NORMAL):

        if not isinstance(code, str):
            raise TypeError(f'Only str type is supported for code, '
                            f'but got {type(code)}')

        if not isinstance(price, float):
            raise TypeError(f'Only float type is supported for price, '
                            f'but got {type(price)}')

        if not isinstance(order_type, str):
            raise TypeError(f'Only str type is supported for order_type, '
                            f'but got {type(order_type)}')

        max_power = {}

        ret, data = self.trade_context.acctradinginfo_query(
            order_type=order_type,
            code=code,
            price=price,
            trd_env=self.trd_env)

        if ret == RET_OK:

            max_power['max_cash_buy'] = data['max_cash_buy'][0]
            max_power['max_cash_and_margin_buy'] = data[
                'max_cash_and_margin_buy'][0]
            max_power['max_position_sell'] = data['max_position_sell'][0]
            max_power['max_sell_short'] = data['max_sell_short'][0]
            max_power['max_buy_back'] = data['max_buy_back'][0]

            return max_power

        else:
            raise RuntimeError('Account trading info query error: ', data)

    def cancel_all_orders(self):

        if self.unlock_trade(self.password):

            if self.paper_trading:

                pending_orders = self.check_today_orders(
                    status_filter_list=['SUBMITTING', 'SUBMITTED'])

                if pending_orders is not None:

                    pending_order_ids = pending_orders['order_id'].to_list()

                    for pending_order_id in pending_order_ids:

                        ret, data = self.trade_context.modify_order(
                            modify_order_op=ModifyOrderOp.CANCEL,
                            order_id=pending_order_id,
                            qty=0,
                            price=0,
                            trd_env=self.trd_env)
                        if ret == RET_OK:
                            print(data)
                        else:
                            print('Error in cancel_all_orders: ', data)

                        time.sleep(0.1)

                else:
                    print('No pending orders exist.')

                self.close_quote_context()
                self.close_trade_context()

            else:

                ret, data = self.trade_context.cancel_all_order(
                    trd_env=self.trd_env, trdmarket=self.filter_trdmarket)
                if ret == RET_OK:
                    print(data)
                else:
                    print('Error in cancel_all_orders: ', data)

                self.close_quote_context()
                self.close_trade_context()

        else:
            print('Unlock trade failed!')
            self.close_quote_context()
            self.close_trade_context()

    def close_trade_context(self):

        self.trade_context.close()

    def close_quote_context(self):

        self.quote_context.close()
